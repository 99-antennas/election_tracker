#!/usr/bin/env python
# coding: utf-8
# Copyright 99 Antennas LLC 2020

import sys
import os
import logging
import json
import datetime as dt
from src.election_fetcher import ElectionsFetcher
from src.utils import CloudStorageClient

# Functions
def run_current_elections():
    """
    Cloud function to run job to fetch election data from Google Civic Information API.
    """
    GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    TODAY = dt.datetime.now()

    logging.info("Starting job fetch elections.")
    get_elections = ElectionsFetcher()
    data = get_elections.fetch_elections()

    # Store data in temp file 
    path = "/tmp/"
    if not os.path.exists(path):
        os.mkdir(path)
    filepath = path + 'data.json'
    
    if data: 
        try: 
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            logging.info(f"Data saved to '{filepath}''")
        except Exception as e: 
            logging.error(e)
    else: 
        logging.error("Error: No data returned.")
        raise
        
    # Upload temp file to Google Gloud Storage
    client = CloudStorageClient()
    bucket_name = "current_elections"
    # Load temp file to gcp as "current_elections.json"
    client.upload_file(filepath, bucket_name, blob_name='current_elections.json')
    # Load temp file to gcp by date
    client.upload_file(filepath, bucket_name, blob_name=f'{TODAY}.json')

    logging.info("Completed job fecth elections.")
# End



