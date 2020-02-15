#!/usr/bin/env python
# coding: utf-8

# Copyright 2017 99 Antennas All Rights Reserved.
"""
Project settings
"""

import os
import datetime as dt

#output meta data
SLUG = "tiller"
ANALYST = os.environ.get('ANALYST')
CONTACT = os.environ.get('CONTACT')
WEBSITE = os.environ.get('WEBSITE')
TODAY = str(dt.datetime.now().date())
PROJECT = "Ad-hoc Reporting"
OUTPUT_PATH = "../output/"
PREPEND_OBJ = "Project:, {} \nLast updated:, {} \nBy:, {} \nContact:, {} \nCode repository:, {}".format(PROJECT, TODAY, ANALYST, CONTACT, WEBSITE) #used for .csv output

#db attribution setting for bulk updates
ATTRIBUTION = 'Bulk update as of {}'.format(TODAY)

#request settings
REQUEST_HEADERS = {'content-encoding': 'gzip',
                'User-Agent': 'Tiller, Simon & Schuster',
                'From': 'kas.stohr@simonandschuster.com'}

#db connection
LOCAL_DB_URI = os.environ.get('LOCAL_DB_URI')
PRODUCTION_DB_URI = os.environ.get('PRODUCTION_DB_URI')
STAGING_DB_URI = os.environ.get('STAGING_DB_URI')

#set default db connection
DB_URI =  STAGING_DB_URI