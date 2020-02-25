#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC

import sys
import os
import logging
import json
import datetime as dt
import time
import base64
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
        
        logging.info(f"Publishing message to {topic_path}")
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

    logging.info(f"Published active elections for current elections as of {str(date)}")


def publish_active_divisions(event, context):
    """
    Publishes parsed election data by division to a Pub/Sub topic with an error handler.
    
    For each division associated with an election, message includes: 
        - election_id=election_id, # As returned by Civic Information API 
        - address=address, # Address of geo division associated with election parsed from locales data.
        - geo_id=geo_id # Fips code or similar geodivision identifier as parsed from locales data
        
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
    logging.info("Starting job to parse election.")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))
    
    # Initiate job
    civic = VoterInfo() 
    
    logging.info("Load addreses by locale")
    locales = civic.load_address_locales("address_locales",  "addresses_county.csv")
    
    project_id = "election-tracker-268319"
    topic_name = "active-divisions"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    futures = dict()
    
    # Parse election 
    if 'attributes' in event: 
        election = event['attributes']
    else: 
        logging.error("Error: Event does not contain attribute data.")
        raise
    election_id = election['election_id'] #renamed to avoid conflict
    election_name = election['name']
    election_ocdid = election['ocdDivisionId']


    # Get state abbr from OCDid
    election_ocdid = election_ocdid.split("/")[-1].split(":")[-1].upper()

    logging.debug(f"election_id: {election_id}")
    logging.debug(f"election_ocdid: {election_ocdid}")
    logging.debug(f"election_name: {election_name}")

    # Subset data by OCDid
    # Except test election 
    if election_name == 'VIP Test Election':
        logging.debug("Election name 'VIP Test Election' excluded.")
        return
    # If election is national, return data for all records
    elif election_ocdid == 'US':
        active = locales.copy()
    # If election is statewide, return data for all records in state. 
    else: 
        active = locales.loc[locales['state_abbr'] == election_ocdid, :].copy()
    # Ensure active elections not null
    try: 
        assert(active.empty == False)
    except Exception as e: 
        logging.error("Unable to subset data by OCDid.")
        raise

    # publish active division
    for index, row in active.iterrows():
        data = str(row["fips"])
        
        logging.info(f"Publishing message to {topic_path}")
        futures.update({data: None})

        # When you publish a message, the client returns a future. Data must be a bytestring.
        future = publisher.publish(
            topic_path, 
            data=data.encode("utf-8"),
            election_id=election_id, 
            address=row['address'], 
            geo_id=str(row["fips"])
        )
        futures[data] = future
        # Publish failures shall be handled in the callback function.
        future.add_done_callback(get_callback(future, data))

    # Wait for all the publish futures to resolve before exiting.
    while futures:
        time.sleep(5)

    logging.info(f"Published active divisions for election {election_id} to {topic_name}")

def run_voter_info(event, context): 
    """
    Retrieves voter information from Google Civic API
    Takes: 
        Data returned from the active-divisons topic message: 
        - election_id=election_id, # As returned by Civic Information API 
        - address=address, # Address of geo division associated with election parsed from locales data.
        - geo_id=geo_id # Fips code or similar geodivision identifier as parsed from locales data
    Makes the API Call 
    Saves the data to Google Cloud Storage
    """
    
    # Job status
    logging.info("Starting job to fetch voter information.")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))
    
    if 'attributes' in event: 
        division = event['attributes']
    else: 
        logging.error("Error: Message does not contain event attributes.")
        raise
    address = division['address']
    geo_id = division['geo_id']
    election_id = division['election_id']
    
    civic = VoterInfo() 
    
    try: 
        logging.info(f"Start VoterInfo call: {election_id}:{geo_id}") 
        response = civic.fetch_voter_info(address, election_id)
        response['geoid'] = {"fips":geo_id}
        civic.save_voter_info(geo_id, response, bucket_name="voter_info")
        time.sleep(1)
        logging.debug(f"Completed VoterInfo call: {election_id}:{geo_id}")
    except Exception as error: 
        logging.error(f"Failed to retrieve data for {election_id}:{geo_id}")
        logging.error(error)