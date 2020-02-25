#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC

import sys
import os
import logging
import json
import datetime as dt
import time
from google.cloud import pubsub_v1
from src.election_fetcher import ElectionsFetcher
from src.voter_info_fetcher import VoterInfo
from src.utils_cloud_storage import CloudStorageClient

# Local testing only 
# GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Functions
def run_current_elections(event, context):
    """
    Cloud function to run job to fetch election data from Google Civic Information API.
    Stores data in a cloud storage bucket as a json file.
    """
    date = dt.datetime.now()
    path = "/tmp/"
    client = CloudStorageClient()
    
    # Job status
    logging.info("Starting job fetch elections.")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))

    # Make API call
    get_elections = ElectionsFetcher()
    data = get_elections.fetch_elections()

    # Store data in temp file
    filename = 'data.json'
    if data:
        client.save_tmp_json(filename, data)
        logging.info("Data saved to temp file.")
    else:
        logging.error("Error: No data returned.")
        return

    # Upload temp file to Google Gloud Storage
    bucket_name = "current_elections"
    filepath = os.path.join(path, filename)
    # Store file as most current
    client.upload_file(filepath, bucket_name, blob_name='current_elections.json')
    # Store file by date
    client.upload_file(filepath, bucket_name, blob_name=f'{date}.json')

    # Job status
    logging.info("Completed job fetch elections.")
    
def publish_active_elections(event, context):
    """
    Publishes elections to Pub/Sub topic with an error handler.
    Data included in attributes of messsage: 
            - election_id=election['id'],
            - name=election['name'], 
            - electionDay=election['electionDay'],
            - ocdDivisionId=election['ocdDivisionId']
    
    """
    def get_callback(f, data):
        def callback(f):
            try:
                logging.info(f.result())
                futures.pop(data)
            except:  # noqa
                logging.info("Please handle {} for {}.".format(f.exception(), data))

        return callback
    
    # Job status
    logging.info("Starting job to publish elections.")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))
    
    # Initiate job
    civic = VoterInfo()
    date = dt.datetime.now().date()
    
    # Load elections data
    logging.info("Load list of current elections.")
    elections = civic.load_current_elections("current_elections",  "current_elections.json")
    
    project_id = "election-tracker-268319"
    topic_name = "active-elections"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    futures = dict()
    
    for election in elections: 
        # Set message attributes 
        
        data = str(election['id'])
        
        # When you publish a message, the client returns a future. Data must be a bytestring.
        futures.update({data: None})
        
        future = publisher.publish(
            topic_path, 
            data=data.encode("utf-8"),
            election_id=election['id'],
            name=election['name'], 
            electionDay=election['electionDay'],
            ocdDivisionId=election['ocdDivisionId']
        )
                                     
        futures[data] = future
        # Publish failures shall be handled in the callback function.
        future.add_done_callback(get_callback(future, data))

    # Wait for all the publish futures to resolve before exiting.
    while futures:
        time.sleep(5)

    print(f"Published active elections for current elections as of {str(date)}")