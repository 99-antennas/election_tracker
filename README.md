# U.S. Election Tracker

Project to get candidate election information from Google Civic Information API. Google Civic Information API offers a number of endpoints that allow the retrieval of election information, including candidate information. However, these endpoints are only accessible for a short window of time before or after a given election. In addition, primary elections are treated as individual elections and candidate information can only be retrieved by address (as opposed to [OCD IDs](https://opencivicdata.readthedocs.io/en/latest/ocdids.html) or other identifier.)

The project includes functions designed to be run as Google Cloud Functions, including: 

- Fetching current, active elections from [Google Civic Information API](https://developers.google.com/civic-information/docs/v2/elections/electionQuery)  
Function: `run_current_elections()
- Reverse geocoding lat/long coordinates to generate address using Google Geocoding API 
- Fetching election information and candidate data from Google Civic Information API 
- Transforming candidate data into longtidy csvs for easier extraction/db load.

## REQUIREMENTS
Python 3.7

Required services: 
- Google Geocoding API 
- Google Civic Information API 
- Google Application Credentials with "Edit" level authorization to the following enabled project resources: 
     - Google Cloud Functions 
     - Google Storage 
     - Permissions to create and manage service accounts
     - Google App Engine (a Google Cloud Scheduler dependancy)
     - Stackdriver (logging)
     
## INSTALLATION

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

## TESTING 

Cloud Functions do not rely on namespace (i.e. `if __name__ == "__main__":`). Therefore to test a function locally, you must ensure the virtual environment is active and invoke the function explicitly. 

```
pipenv run python -c 'from main import run_current_elections; run_current_elections()'
```

## SETUP

1. Create a project (or select an existing project)
2. Create a service account key and download it to the project directory. 
Roles: `Cloud Functions Editor`, `Source Editor`, `Service Account Actor`, `Cloud Storage Editor` 
3. Store the  .json file to your local environment as `GOOGLE_APPLICATION_CREDENTIALS`  Note: If the file is not automatically discovered by GCloud and you get authentication errors, you may need to set a local environment variable to ensure the file is on your path. 

```
export GOOGLE_APPLICATION_CREDENTIALS="absolute/path/to/credentials.json"
```
4. Write the function, test it locally, then add it to the deploy.sh file with a trigger (http, pub-sub topic, bucket).
5. Sync your github repo with a Cloud Source Repository
6. Commit and push your changes to Github

## DEPLOYMENT 

Create and deploy the Cloud Function and dependent Google Cloud resources by running the deployment shell script from your local terminal: 

**IMPORTANT: Commit and push your changes to Github before each deploy.** 

```
sh ./bin/deploy.sh
```
The script will: 

1. Load environment variables from the .env file and deploy them as key, value pairs to the Cloud Function for testing (** IMPORTANT: Secrets should NOT be stored as environment variables, and should be retrieved from a separate source at runtime or called in the code.**)  
2. Create a requirements.txt file based on the Pipfile. Required by Cloud Functions for deployment. (Note: this will include development packages unfortunately. They should be removed or commented out prior to deployment to avoid exceeding memory limitations (256MB)) 
3. Create Cloud Storage buckets (Note: If buckets exist this will generate an error - Ignore)
4. Sets the Google Cloud project in the local config file to ensure changes are applied to the right project.
5. Sets the projects default region/zone so that resources are in the same region
6. Defines and create PubSub topic (Note: If topic exist this will generate an error - Ignore) 
7. Defines adn deploys the Google CLoud Function 


## SAMPLE DATA

[/test/sample_data/](/test/sample/data)

## OTHER GUIDANCE
- [Google Cloud SDK Python](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python)
- [gcloud deployment commands](https://cloud.google.com/sdk/gcloud/reference/)
- [Granting Roles to Service Accounts](https://cloud.google.com/iam/docs/granting-roles-to-service-accounts)
- [Authenticating Apps in Production](https://cloud.google.com/docs/authentication/production)
- [Mirroring a Github Repo](https://cloud.google.com/source-repositories/docs/mirroring-a-github-repository)
- [Deploying a Cloud Function](https://hackingandslacking.com/creating-google-cloud-functions-running-python-3-7-8034e066a130)
- [Cloud Function Runtime Environment](https://cloud.google.com/functions/docs/concepts/exec)
- [Cloud Function Quotas](https://cloud.google.com/functions/quotas)
- [Using Cloud Pub-Sub and Scheduler to trigger a Cloud Function](https://cloud.google.com/scheduler/docs/tut-pub-sub)
- [Cron Commands](http://man7.org/linux/man-pages/man5/crontab.5.html)
- [How to use Pub-sub message attributes](https://stackoverflow.com/questions/54950178/how-to-use-pub-sub-message-attributes-in-cloud-scheduler) 


## TODOs
- PyTest Unit Tests
- Setup Secrets manager
- Rotate API keys
- Add additional Cloud Functions
- Convert deploy.sh to yaml

## SUGGESTING CHANGES
If you have suggestions, please submit a pull request.