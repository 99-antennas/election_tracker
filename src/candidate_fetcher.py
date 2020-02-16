"""
Fetch elections from the Google Civic API
"""

import os
import json
import logging
import requests

class ElectionsFetcher(): 
    """
    Fetchs a list of current elections from Google Civic Information API
    https://developers.google.com/civic-information/docs/v2/elections/electionQuery 
    
    Returns the response as a json object.
    """
    
    def __init__(self):
        self._url = "https://www.googleapis.com/civicinfo/v2/elections"
        self._api_key = os.environ["GOOGLE_CIVIC_API_KEY"]

    def fetch_elections(self):
        """
        Make a call to the api to return election info
        """
        payload = {"key": self._api_key} 
        response = requests.get(self._url, params=payload)
        try: 
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as error:
            # Error in request 
            logging.error(error)
        except requests.exceptions.RequestException as error:
            # Catastrophic error 
            logging.error(error)
            raise

class CloudStorageClient():
    """
    Stores files on Google Cloud Storage
    """
    def __init__(self):
        try: 
            self.client = storage.Client()
            logging.info("Connected to Google Cloud Storage.")
        except Exception as error: 
            logging.error("Error connecting to Google Cloud Storage:")
            logging.error(error)
            
    def upload_file(self, filepath, bucket_name, blob_name):
        try: 
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            with open(filepath, 'rb') as file:
                blob.upload_from_file(file)
            logging.info(f"Loaded file {filepath} to {blob_name}")
        except Exception as error: 
            logging.error("Error storing the file to Google Cloud Storage:")
            logging.error(error)
            
# End
