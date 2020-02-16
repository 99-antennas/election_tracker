#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 99 Antennas LLC 

"""
Fetch elections info and candidate data from Google Civic API
"""

import os
import json
import logging

import pandas as pd
import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from nameparser import HumanName
from newsapp.models import Candidate


class District():
    def __init__(self, name, kg_foreign_key):
        self.name = name
        self.kg_foreign_key = kg_foreign_key


class Contest():
    """
    A contest in the election
    """

    def __init__(self, office, district):
        self.office = office
        self.district = district


class CandidateCreator():
    """
    Fetches candidate data from the Google Civic API,
    converts it into Candidate objects, and saves to the db
    """

    def __init__(self):
        self._url = "https://www.googleapis.com/civicinfo/v2/voterinfo"
        self._api_key = os.environ["GOOGLE_CIVIC_API_KEY"]

        # ID for the US 2018 Midterm Election
        self._election_id = 6000

    def create_candidates_from_response(self, response):
        """
        Convert the json response from the api into a candidate list
        """

        try:
            # a missing key may mean this data hasn't been populated yet
            contests = response["contests"]
        except KeyError:
            return []

        for contest in contests:
            try:
                office = contest["office"]
                candidates = contest["candidates"]
            except KeyError:
                # some contests, such as referendums, may not have an office or candidates
                # alternatively, we might filter by the type of contest
                continue

            self.create_candidates(
                candidate_list=candidates,
                contest=Contest(
                    office=office,
                    district=District(
                        name=contest["district"]["name"],
                        kg_foreign_key=contest["district"].get(
                            "kgForeignKey", "")
                    )
                )
            )

    def create_candidates(self, candidate_list, contest):
        """
        Construct a list of candidates running for a particular office
        """

        for c in candidate_list:
            human_name = HumanName(c["name"])

            # get_or_create is failing, and I don't know why
            try:
                Candidate.objects.get(full_name=human_name.full_name)
            except Candidate.DoesNotExist:
                twitter_id, fb_id = self.get_social_channels(
                    c.get("channels", ""))

                Candidate(
                    full_name=human_name.full_name,
                    first_name=human_name.first,
                    last_name=human_name.last,
                    middle_initial=human_name.middle[0] if human_name.middle else '',
                    suffix=human_name.suffix,
                    ocd_id=contest.district.kg_foreign_key,
                    office=contest.office,
                    phone=c.get("phone", ""),
                    email=c.get("email", ""),
                    twitter_id=twitter_id,
                    facebook_id=fb_id,
                    party=c.get("party", "")
                ).save()

    def fetch_civic_data(self, address):
        """
        Make a call to the api to return election info for an address
        """
        payload = {"address": address,
                   "key": self._api_key,
                   "electionId": self._election_id,
                   # "fields": "contests"
                   }

        return requests.get(self._url, params=payload)

    def get_social_channels(self, channels):
        """
        Get Facebook and Twitter ids from json
        """
        twitter_id, fb_id = "", ""

        if channels:
            for channel in channels:
                if channel["type"] == "Twitter":
                    twitter_id = channel["id"]
                elif channel["type"] == "Facebook":
                    fb_id = channel["id"]

        return twitter_id, fb_id


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("address",
                            type=str,
                            help="The address to query for candidates",
                            nargs="?",
                            default=None)

    def handle(self, *args, **options):
        locales_csv = os.path.join(settings.NEWSAPP_CSVS_DIR, "locales.csv")
        df = pd.read_csv(locales_csv)

        creator = CandidateCreator()

        # if an address is passed as an arg, create candidates for that address
        # otherwise, create candidates from all addresses in the locales csv
        if options["address"]:
            creator.create_candidates_from_response(
                json.loads(creator.fetch_civic_data(options["address"]).text))
        else:
            for address in df["office_address"]:
                response = creator.fetch_civic_data(address)
                creator.create_candidates_from_response(
                    json.loads(response.text))
