#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC

import sys
import os
import logging
import json
import datetime as dt
import time
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
    
def run_pub_election(): 
    """
    Cloud function to run job to parse voter information data for current elections
    from Google Civic Information API.
    Retrieves county level data and sets the fips code as the identifier (`geo_id`)
    Stores data in a cloud storage bucket as a json file.
    """
    # Job status
    logging.info("Starting job fetch voter information")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))
    
    # Initiate job
    civic = VoterInfo() 
    
    # Load elections, address data
    logging.info("Load list of current elections.")
    elections = civic.load_current_elections("current_elections",  "current_elections.json")
    
    # Retrieve Voter information data
    for election in elections:
        election_id = election['id']
        election_name = election['name']
        election_ocdid = election['ocdDivisionId']
        
        # Get state abbr from OCDid
        election_ocdid = election_ocdid.split("/")[-1].split(":")[-1].upper()

        logging.debug(f"election_id: {election_id}")
        logging.debug(f"election_ocdid: {election_ocdid}")
        logging.debug(f"election_name: {election_name}")


def run_voter_info(event, context): 
    
    """
    Cloud function to run job to parse voter information data for current elections
    from Google Civic Information API.
    Retrieves county level data and sets the fips code as the identifier (`geo_id`)
    Stores data in a cloud storage bucket as a json file.
    """
    
    # Job status
    logging.info("Starting job fetch voter information")
    logging.info("""Trigger: messageId {} published at {}""".format(context.event_id, context.timestamp))
    
    # Initiate job
    civic = VoterInfo() 
    
    # Load elections, address data
    logging.info("Load list of current elections.")
    elections = civic.load_current_elections("current_elections",  "current_elections.json")
    
    logging.info("Load addreses by locale")
    locales = civic.load_address_locales("address_locales",  "addresses_county.csv")
    
    # Retrieve Voter information data
    for election in elections:
        election_id = election['id']
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
            continue
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
    
        # Get voter information for election
        try: 
            logging.info(f"Start election: {election_id}:{election_ocdid}") 
            for index, row in active.iterrows():
                address = row['address']
                geo_id = row["fips"]
                response = civic.fetch_voter_info(address, election_id)
                response['geoid'] = {"fips":geo_id}
                civic.save_voter_info(geo_id, response, bucket_name="current_contests")
                time.sleep(1)
            logging.debug(f"Completed election: {election_id}:{election_ocdid}")
        except Exception as error: 
            logging.error(f"Failed to retrieve data for {election_id}:{election_ocdid}")
            logging.error(error)
    
    # Job status
    logging.info("Completed job fetch voter info.")
# End
