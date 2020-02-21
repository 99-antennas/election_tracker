#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC 

"""
Script to setup project Google Cloud Storage buckets. 
https://cloud.google.com/storage/docs/xml-api/put-bucket-create
"""

import os
import logging
from google.cloud import storage

GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Instantiates a client
storage_client = storage.Client()

# Names for new buckets
bucket_names = ["current_elections", "address_locales", "current_candidates", "current_contests"]

# Creates the new bucket
for name in bucket_names: 
    try: 
        bucket = storage_client.create_bucket(name)
        logging.info(f"Bucket {bucket.name} created.")
    except Exception as e: 
        logging.error(f"Failed to create bucket: {name}")
        logging.error(e)
# End
