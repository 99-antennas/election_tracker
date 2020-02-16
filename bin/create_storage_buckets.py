import os
import logging
from google.cloud import storage

GOOGLE_APPLICATION_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = "current_elections"

# Creates the new bucket
try: 
    bucket = storage_client.create_bucket(bucket_name)
    logging.info(f"Bucket {bucket.name} created.")
except Exception as e: 
    logging.error(e)
