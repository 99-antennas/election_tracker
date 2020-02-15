# Jupyter Notebook Template -  Analysis 

Tiller data science template notebook and sample data for creating presentation-level notebook output. For more guidance refer to the [Data Science Team Handbook](https://docs.google.com/document/d/1nliyytDx42_rSIfrXCONnEm9-YqIDsBvWx1DkZDHJV0/edit)

REQUIREMENTS  
Python 3.7

INSTALLATION  

1. Check to see if a version of the repo exists on your computer.
If it does NOT exist:

```
git clone  https://github.com/snsdigitaldevs/ds_template_jupyter_notebook.git
```
If it exists:

```
cd path/to/aaa_jupyter_template
git pull origin master
```

2. Create a .env file
Follow the [sample_env](sample_env) file included in the repo to set the default settings for your presentation notebook. 
- 

```
touch .env
```

Add the following to the file:

```
ANALYST="First Name Last Name"<br>
CONTACT="Your Email"<br>
WEBSITE="https://github.com/orgs/snsdigitaldevs/teams/tiller"<br>
PROJECT="approved_project_slug" 
```

Note: There is only one project slug for any given project. If you are unsure of the project slug, please ask. 

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
The repo includes two sample data sets for testing. 

Sample data sets: 
- [Goodreads-books](https://www.kaggle.com/jealousleopard/goodreadsbooks#books.csv)
- [Titanic: Machine Learning from Disaster](https://www.kaggle.com/c/titanic/data)
- [Twitter Sentiment Analysis](https://www.kaggle.com/arkhoshghalb/twitter-sentiment-analysis-hatred-speech)  
Detecting hatred tweets, data provided by Analytics Vidhya

Source: Kaggle


GUIDANCE  
In preparing presentation notebooks: 
- separate pre-processing steps into a separate notebook
- **All proprietoary data** must be stored on the cloud or in a database and not in the notebook repo. The only data stored in the data folder should be static publically accessible data, such as Census data, map shape files, cross-walk files, etc. 
- **No proprietary data should be committed to Github** 
- output .csv's should include pre-pended meta data that enables us to track the source, purpose and date the file was created in the future. Tip: Use `skiprows` to easily load csv's with pre-pended metadata. 


SUGGESTING CHANGES  
If you have changes to the notebooks and would like to share them with the rest of the team, please submit a pull request. 

