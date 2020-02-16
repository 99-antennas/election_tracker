# U.S. Election Tracker

Project to get candidate election information from Google Civic Information. Google Civic Information offers a number of endpoints that allow the retrieval of election information, including candidate information. However, these endpoints are only accessible for a short window of time before or after a given election. In addition, primary elections are treated as individual elections and candidate information can only be retrieved by address (as opposed to [OCD IDs](https://opencivicdata.readthedocs.io/en/latest/ocdids.html) or other identifier.)

The project includes functions designed to be run as Google Cloud Functions, including: 

- Fetching current, active elections from Google Civic Information API 
Function: `run_current_elections()`
https://developers.google.com/civic-information/docs/v2/elections/electionQuery

- Reverse geocoding lat/long coordinates to generate address using Google Geocoding API 

- Fetching election information and candidate data from Google Civic Information API 

REQUIREMENTS
Python 3.7

Required services: 
- Google Geocoding API 
- Google Civic Information API 
- Google Application Credentials (roles and permissions)
     - Google Cloud Functions 
     - Google Storage 
     - Permissions to create and manage service accounts
     
INSTALLATION

1. Clone the repo

```
git clone  https://github.com/99-antennas/election_tracker.git
```
2. Create a .env file
Follow the [sample_env](sample_env) file included in the repo to set the required credentials.
-

```
touch .env
```

Paste the following credentials into your .env file.   

```
GOOGLE_CIVIC_API_KEY="your-api-key"
GOOGLE_GEOCODING_API_KEY="your-api-key"

```
Save and close the .env file.
IMPORTANT: Check the .gitignore file to ensure that the .env file will not be committed.

3. Initiate your virtual environment

```
pipenv install --three
```
Use the '--three' flag to indicate Python 3 if you have more than one interpreter installed. If promptedl, load the packages as they appear by the name in the prompt.

```
pipenv install PACKAGE NAME

```

4. Launch the virtual environment shell

```
pipenv shell
```

5. Launch Jupyter notebook

(Jupyter Labs or Notebooks are helpful for testing data extractions and transforms but not required.)

```
jupyter lab
```

TESTING 

Cloud Functions do not rely on namespace (i.e. `if __name__ == "__main__":`). Therefore to test a function locally, you must ensure the virtual environment is active and invoke the function explicitly. 

```
pipenv run python -c 'from main import run_current_elections; run_current_elections()'
```

DEPLOYMENT 

1. Create a requirements.txt file based on the Pipfile 

Cloud Functions depend on requirements.txt to deploy. Run the following command: 

```
pipenv lock -r > requirements.txt
```
Note this will include development packages unfortunately. So they may need to be removed prior to deployment to avoid exceeding memory limitations (256MB)

2. Create a service account key and download it to the project directory. 
Roles: `Cloud Functions Editor`, `Source Editor`, `Service Account Actor`, `Cloud Storage Editor` 

Store the path to the service account .json file in your .env file as `GOOGLE_APPLICATION_CREDENTIALS`

3. Create the necessary Cloud Storage buckets

```
pipenv run python ./bin/create_storage_buckets.py
```

4. Deploy the cloud function

Add function to the deploy.sh file with either http trigger or pub-sub topic and run file.

```
sh ./bin/deploy.sh
```

SAMPLE DATA

[/test/sample_data/](/test/sample/data)

OTHER GUIDANCE
[Google Cloud SDK Python](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python)
[Deploying a Cloud Function](https://hackingandslacking.com/creating-google-cloud-functions-running-python-3-7-8034e066a130)
[Granting Roles to Service Accounts](https://cloud.google.com/iam/docs/granting-roles-to-service-accounts)
[Authenticating Apps in Production](https://cloud.google.com/docs/authentication/production)


SUGGESTING CHANGES
If you have suggestions, please submit a pull request.

