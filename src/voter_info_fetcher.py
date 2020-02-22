#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC

"""
Fetch voter info from Google Civic Information API
"""
import sys
import os
import logging
import json
import datetime as dt
import pandas as pd
import requests
from google.cloud import storage
from src.utils_cloud_storage import CloudStorageClient


class ReverseGeocode(): 
    """
    Fetchs a address and geocoding data from Google Geocoding API. 
    Takes the lat, long as geo points.
    Returns the address as a json object of a list of formatted addresses.
    Documentation: 
    https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding 
    https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=YOUR_API_KEY
    """
    
    def __init__(self):
        self._url = "https://maps.googleapis.com/maps/api/geocode/json?"
        self._api_key = os.environ['GOOGLE_GEOCODING_API_KEY']
    
    def reverse_geocode(self, lat, long):
        """
        Make a call to the api to return election info
        """
        payload = {
            "latlng": f"{lat},{long}",
            "key": self._api_key
        } 
        response = requests.get(self._url, params=payload)
        try: 
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as error:
            # Error in request 
            logging.error(error)
            return 0
        except requests.exceptions.RequestException as error:
            # Catastrophic error 
            logging.error(error)
            raise

class VoterInfo():
    """
    Fetchs voter information from Google Civic Information API.
    Takes a correctly formatted address and returns the available election information. 
    If not election Id is provided, returns the election(s) for which information is available.
    The returned information *may* include: 
        - "pollingLocations" = Polling places (including early polling sites) for a given residential street address
        - "contests" = Contest and candidate information
        - "state" = Election official information

    Documentation: 
    https://developers.google.com/civic-information/docs/v2/elections/voterInfoQuery
    https://developers.google.com/civic-information/docs/v2/standard_errors
    """
    
    def __init__(self):
        self._url = "https://www.googleapis.com/civicinfo/v2/voterinfo"
        self._api_key = os.environ['GOOGLE_CIVIC_API_KEY']
        self.date = dt.datetime.now().date()
        self.client = CloudStorageClient()
        self.path = "/tmp/"
        if not os.path.exists(self.path):
            os.mkdir(self.path)
    
    def fetch_voter_info(self, address, election_id=None):
        """
        Make a call to the api to return election info
        """
        payload = {
            "address": address, 
            "electionId": election_id,
            "returnAllAvailableData": True,
            "key": self._api_key
        } 
        response = requests.get(self._url, params=payload)
        try: 
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as error:
            # Error in request 
            logging.error(f"Error: CivicInfo Api error for {address}")
            logging.error(error)
            raise
        except requests.exceptions.RequestException as error:
            # Catastrophic error 
            logging.error(f"Fail: CivicInfo Api failed for {address}")
            logging.error(error)
            raise
            
    def save_voter_info(self, geoid, result, bucket_name):
        """
        Takes: 
            - a geoid such as a county fips code or OCDid or other identifier as filename.
            - the data returned for the geoid
        Saves the file to the project bucket. 
        """
        blob_name = geoid + "_" + str(self.date) + '.json'
        filepath = os.path.join(self.path, blob_name)
        try: 
            self.client.save_tmp_json(blob_name, result)
            self.client.upload_file(filepath, bucket_name, blob_name)
            logging.error(f"Successfully saved data for {geoid} to: gs://{bucket_name}/{blob_name}")
        except Exception as error: 
            logging.error(f"Error uploading data for {geoid} to gs://{bucket_name}/{bucket_name}.")
            logging.error(error)
            
    def load_current_elections(self, bucket_name, blob_name): 
        """
        Load json file listing current elections. 
        Validates 'elections' data in file
        Takes: 
        - bucket name 
        - blob name of file 
        
        Returns: election data as json list
        """ 
        filepath = os.path.join(self.path, blob_name)
        
        #load data from Google Cloud Storage  
        self.client.download_file(filepath, bucket_name, blob_name)
        data = self.client.load_tmp_json(filepath)

        try: 
            elections = data['elections']
            logging.info("Successfully loaded current elections data.")
            return elections
        except KeyError as error: 
            logging.error(f"There are no current elections stored in file: 'gs://' {bucket_name} + '/' + {blob_name}")
            raise
        except Exception as error: 
            logging.error(f"Error loading current elections from file: 'gs://' {bucket_name} + '/' + {blob_name}")
            logging.error(error)
            raise
            
    def load_address_locales(self, bucket_name, blob_name): 
        filepath = os.path.join(self.path, blob_name)

        #load temp file to gcp  
        self.client.download_file(filepath, bucket_name, blob_name)

        #load address data
        try: 
            with open(filepath, 'rb') as file:
                data = pd.read_csv(filepath, encoding='utf-8')
            logging.debug(f"Loaded address data from {filepath}")
        except Exception as error: 
            logging.error("Failed to load address data from /tmp/.")

        try: 
            #process data - ensure necessary columns available
            addresses = data['address']
            state_abbr = data['state_abbr']
            data['fips'] = data['fips'].astype('str').str.zfill(5)
            logging.info("Successfully loaded address lookup data.")
            return data
        except KeyError as error: 
            logging.error(f"There are no current elections stored in file: 'gs://' {bucket_name} + '/' + {blob_name}")
            raise
        except Exception as error: 
            logging.error(f"Error loading current elections from file: 'gs://' {bucket_name} + '/' + {blob_name}")
            logging.error(error)
            raise
            
# End
