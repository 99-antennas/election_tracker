#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC 

import sys
import os
import logging
import json
import datetime as dt

from google.cloud import storage

class CloudStorageClient():
    """
    Stores files on Google Cloud Storage
    """
    def __init__(self):
        """
        Opens Google Cloud Storage connection. 
        Creates root /tmp/ directory.
        """
        try: 
            self.client = storage.Client()
            logging.debug("Connected to Google Cloud Storage.")
        except Exception as error: 
            logging.error("Error connecting to Google Cloud Storage:")
            logging.error(error)
            
        try: 
            self.path = "/tmp/"
            if not os.path.exists(self.path):
                os.mkdir(self.path)
        except Exception as error: 
            logging.error(f"Failed to create dir {self.path}")
            logging.error(error)
            
    def upload_file(self, filepath, bucket_name, blob_name):
        """
        Uploads a files from a local directory to Google Cloud Storage. 
        Takes: 
        - filepath to the file stored locally 
        - bucket name on Google Cloud Storage 
        - blob_name on Google Cloud Storage
        """
        try: 
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            with open(filepath, 'rb') as file:
                blob.upload_from_file(file)
            logging.debug(f"Successfully loaded file from {filepath} to {blob_name}")
        except Exception as error: 
            logging.error("Error storing the file to Google Cloud Storage:")
            logging.error(error)
    
    def download_file(self, filepath, bucket_name, blob_name):
        """
        Downloads a files from Google Cloud Storage to a local directory. 
        
        Takes: 
        - filepath where the file should be stored locally 
        - bucket name on Google Cloud Storage 
        - blob_name on Google Cloud Storage
        """
        try: 
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            with open(filepath, 'wb') as file:
                blob.download_to_file(file)
            logging.debug(f"Downloaded file from gs://{bucket_name}/{blob_name} to {filepath}")
        except Exception as error: 
            logging.error("Error retreiving the file from Google Cloud Storage.")
            logging.error(error)
        
    def save_tmp_json(self, filename, data):
        """
        Temporarily stores json as a local temp file to /tmp/.
        """
        try: 
            logging.debug("Saving json... ")
            filepath = os.path.join(self.path, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            logging.debug(f"Successfully saved json to {filepath}.")
        except Exception as error: 
            logging.error(f'Failed to save json to {self.path}')
            logging.error(error)
    
    def load_tmp_json(self, filename):
        """
        Retrieves json from local temp file in /tmp directory.  
        """
        try: 
            logging.debug("Loading json... ")
            filepath = os.path.join(self.path, filename)
            with open(filepath, 'rb') as file:
                data = json.load(file)
            logging.debug(f"Successfully loaded json from {filepath}.")
            return data
        except Exception as error: 
            logging.error(f'Failed to load json from {os.path.join(self.path, filename)}')
            logging.error(error)