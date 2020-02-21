#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC

import sys
import os
import logging
import json
import datetime as dt
from src.election_fetcher import ElectionsFetcher
from src.utils import CloudStorageClient

# Functions
def run_current_elections(event, context):
    """
    Cloud function to run job to fetch election data from Google Civic Information API.
    Stores data in a cloud storage bucket as a json file.
    """
    # Local testing only 
    # GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    
    date = dt.datetime.now()
    client = CloudStorageClient()
    
    # Job status
    logging.info("Starting job fetch elections.")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))

    # Make API call
    get_elections = ElectionsFetcher()
    data = get_elections.fetch_elections()

    # Store data in temp file
    if data:
        client.save_tmp_json('data.json', data)
        logging.info(f"Data saved to '{filepath}''")
    else:
        logging.error("Error: No data returned.")
        return

    # Upload temp file to Google Gloud Storage
    bucket_name = "current_elections"
    # Store file as most current
    client.upload_file(filepath, bucket_name, blob_name='current_elections.json')
    # Store file by date
    client.upload_file(filepath, bucket_name, blob_name=f'{date}.json')

    # Job status
    logging.info("Completed job fetch elections.")
# End
