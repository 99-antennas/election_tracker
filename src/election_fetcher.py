"""
Fetch elections from the Google Civic API
"""
import sys
import os
import logging
import json
import requests
from google.cloud import storage

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
            
# End
