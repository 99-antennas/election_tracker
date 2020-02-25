### Script for deploying Cloud Function ###

# Load environment variables
source .env
export GCP_FUNCTION_NAME=PubActiveDivisions
export GCP_FUNCTION_ENTRY_POINT=publish_active_divisions
export TRIGGER_PUBSUB_TOPIC=active_elections
export GCP_PUBSUB_TOPIC=active-divisions

# Create requirements.txt
# Note: syncs without re-locking and updating packages
pipenv sync
pipenv run pip freeze > requirements.txt

# Create Cloud bucket
# Not Applicable

# Set Google Cloud project
gcloud --quiet config set project $GCP_PROJECT_NAME

# If not default, set region/zone
gcloud --quiet config set compute/zone ${GCP_COMPUTE_ZONE}

# Create PubSub topic
# Note: If topic exist this will generate an error - Ignore
gcloud pubsub topics create $GCP_PUBSUB_TOPIC

# Deploy function 
# https://cloud.google.com/sdk/gcloud/reference/functions/deploy
# Add #--retry \ once tested
gcloud functions deploy $GCP_FUNCTION_NAME \
--source https://source.developers.google.com/projects/$GCP_PROJECT_NAME/repos/$GCP_REPOSITORY_ID \
--runtime python37 \
--trigger-topic $TRIGGER_PUBSUB_TOPIC \
--entry-point $GCP_FUNCTION_ENTRY_POINT \
--service-account api-requests@election-tracker-268319.iam.gserviceaccount.com \
--set-env-vars GOOGLE_CIVIC_API_KEY=$GOOGLE_CIVIC_API_KEY,GOOGLE_GEOCODING_API_KEY=$GOOGLE_GEOCODING_API_KEY

#End
