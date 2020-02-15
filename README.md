# U.S. Election Tracker

Project to get candidate election information from Google Civic Information. Google Civic Information offers a number of endpoints that allow the retrieval of election information, including candidate information. However, these endpoints are only accessible for a short window of time before or after a given election. In addition, primary elections are treated as individual elections and candidate information can only be retrieved by address (as opposed to OCD-ID or other identifier.)

REQUIREMENTS
Python 3.7

INSTALLATION

1. Check to see if a version of the repo exists on your computer.
If it does NOT exist:

```
git clone  https://github.com/99-antennas/election_tracker.git
```
If it exists:

```
cd path/to/election_tracker
git pull origin master
```

2. Create a .env file
Follow the [sample_env](sample_env) file included in the repo to set the required credentials.
-

```
touch .env
```

Add the following to the file:

```

```
Save and close the .env file.

3. Initiate your virtual environment

```
pipenv install --three
```
Use the '--three' flag to indicate Python 3 if you have more than one interpreter installed.


At this point you may be prompted to load packages. Load the packages that appear by the name in the prompt

```
pipenv install PACKAGE NAME

```

4. Launch the virtual environment shell

```
pipenv shell
```

5. Launch Jupyter notebook

```
jupyter notebook
```

SAMPLE DATA


GUIDANCE


SUGGESTING CHANGES
If you have suggestions, please submit a pull request.

