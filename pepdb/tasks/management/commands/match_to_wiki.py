# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from time import sleep
from django.core.management.base import BaseCommand
from django.conf import settings

import tqdm
from elasticsearch_dsl import Q

import requests
from requests.exceptions import RequestException

from core.utils import is_cyr, is_ukr, is_greek, is_eng
from core.models import Person
from tasks.models import WikiMatch


class Command(BaseCommand):
    help = "Search PEPs in wikidata DB and prepare tasks for matching"

    def search_by_name(self, name, lang=["uk"]):
        try:
            if not lang:
                lang = []
                if is_cyr(name):
                    lang.append("ru")
                    lang.append("uk")

                if is_greek(name):
                    lang.append("el")

                if is_eng(name):
                    lang.append("en")

            ids = set()

            for l in lang:
                resp = requests.get(
                    "https://www.wikidata.org/w/api.php",
                    params={
                        "action": "wbsearchentities",
                        "search": name,
                        "language": l,
                        "format": "json",
                    },
                    timeout=60
                )

                for r in resp.json().get("search", []):
                    ids.add(r["id"])

            return ids
        except RequestException as e:
            self.stderr.write("Cannot get a response for name {}, error message is {}".format(name, e))
            return set()

    def fetch_details(self, ids):
        responses = []
        for id_ in ids:
            resp = requests.get(
                "https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(id_),
                timeout=60
            ).json()
            if resp.get("entities", {}).get(id_):
                responses.append(resp.get("entities", {}).get(id_))

        return responses

    def add_arguments(self, parser):
        parser.add_argument(
            '--deep_search',
            default=False,
            action="store_true",
            help='Use also all generated transliterated names to search',
        )

    def handle(self, *args, **options):
        q = Person.objects.all()
        created_matches = 0
        not_found_matches = 0
        not_found_shallow_matches = 0
        updated_matches = 0

        with tqdm.tqdm(total=q.count()) as pbar:
            for p in q.nocache().iterator():
                pbar.update(1)
                ids = self.search_by_name(p.full_name, ["uk"])
                ids |= self.search_by_name(p.full_name_en, ["en"])

                if not ids:
                    not_found_shallow_matches += 1

                if p.also_known_as_uk:
                    for aka_name in filter(None, p.also_known_as_uk.split("\n")):
                        ids |= self.search_by_name(aka_name, None)

                if p.also_known_as_en:
                    for aka_name in filter(None, p.also_known_as_en.split("\n")):
                        ids |= self.search_by_name(aka_name, None)

                if not ids:
                    for name in filter(None, p.names.split("\n")):
                        # Trying just russian translations if deep search is off
                        if options["deep_search"] or is_cyr(name):
                            ids |= self.search_by_name(name, None)
                            sleep(0.1)

                if not ids:
                    not_found_matches += 1
                    continue

                details = self.fetch_details(ids)

                obj, created = WikiMatch.objects.get_or_create(
                    person_id=p.id,
                    defaults={
                        "pep_name": p.full_name,
                        "pep_position": "{} @ {}".format(
                            getattr(p, "last_job_title", ""),
                            getattr(p, "last_workplace", ""),
                        ),
                        "matched_json": details
                    },
                )

                if not created:
                    updated_matches += 1
                    obj.matched_json = details
                    obj.save()
                else:
                    created_matches += 1

        self.stdout.write(
            "Created: {}\nUpdated: {}\nNot found by name: {}\nNot found at all: {}".format(
                created_matches,
                updated_matches,
                not_found_shallow_matches,
                not_found_matches
            )
        )
