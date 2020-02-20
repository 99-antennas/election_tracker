#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC 

"""
Fetch candidates info from Google Civic Information API
"""
import sys
import os
import logging
import json
import requests
from google.cloud import storage


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
            
# End
