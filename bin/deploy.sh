### Script for deploying Cloud Function ###

# Load environment variables
source .env

# Create requirements.txt 
pipenv sync
pipenv run pip freeze

# Create Cloud buckets 
# Note: If buckets exist this will generate an error
pipenv run python ./bin/create_storage_buckets.py

# Deploy function 
# https://cloud.google.com/sdk/gcloud/reference/functions/deploy
# Add #--retry \ once tested

gcloud functions deploy FetchElections \
--source https://source.cloud.google.com/projects/election-tracker-268319/repos/github_99-antennas_election_tracker \
--runtime = python37 \
--trigger-topic = CivicInfoAPI_elections \
--entry-point = run_current_elections \
--service-account = api-requests@election-tracker-268319.iam.gserviceaccount.com \
--set-env-vars=[GOOGLE_CIVIC_API_KEY=$GOOGLE_CIVIC_API_KEY,GOOGLE_GEOCODING_API_KEY=$GOOGLE_GEOCODING_API_KEY]
