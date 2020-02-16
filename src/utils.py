#!/usr/bin/env python
# coding: utf-8
# Copyright 99 Antennas LLC 2020

import sys
import os
import logging
import json
from google.cloud import storage

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