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
    # Local testing Only 
    # GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    TODAY = dt.datetime.now()

    # Job status
    logging.info("Starting job fetch elections.")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))

    # Make API call
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
            raise
    else:
        logging.error("Error: No data returned.")
        return

    # Upload temp file to Google Gloud Storage
    client = CloudStorageClient()
    bucket_name = "current_elections"
    # Store file as most current
    client.upload_file(filepath, bucket_name, blob_name='current_elections.json')
    # Store file by date
    client.upload_file(filepath, bucket_name, blob_name=f'{TODAY}.json')

    # Job status
    logging.info("Completed job fetch elections.")
# End
