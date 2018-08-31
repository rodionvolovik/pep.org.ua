# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from time import sleep
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.translation import activate

from dateutil.parser import parse as dt_parse
import tqdm
from elasticsearch_dsl import Q

from core.utils import render_date
from core.models import Person
from tasks.models import AdHocMatch


class Command(BaseCommand):
    help = "Add data from matches with central election comitee data to the PEP db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--real_run",
            default=False,
            action="store_true",
            help="Add matched data to wiki articles",
        )

    def handle(self, *args, **options):
        q = AdHocMatch.objects.filter(dataset_id="cvk_2015", applied=False, status="a")

        dob_mismatch = 0
        dob_updated = 0
        wiki_updated = 0
        activate(settings.LANGUAGE_CODE)

        with tqdm.tqdm(total=q.count()) as pbar:
            for match in q.select_related("person").nocache().iterator():
                pbar.update(1)

                if not match.person:
                    continue

                dob = match.person.date_of_birth
                new_dob_dt = dt_parse(match.matched_json["dob"], dayfirst=True)

                if not dob:
                    match.person.dob = new_dob_dt
                    match.person.dob_details = 0
                    dob_updated += 1
                else:
                    new_dob = render_date(new_dob_dt, match.person.dob_details)

                    if dob != new_dob:
                        self.stderr.write(
                            "DOB mismatch for profile {}{}, current {}, new {}, CVK details {}".format(
                                settings.SITE_URL,
                                match.person.get_absolute_url(),
                                dob,
                                render_date(new_dob_dt, 0),
                                match.matched_json["url"]
                            )
                        )
                        dob_mismatch += 1
                        continue

                    if match.person.dob_details > 0:
                        match.person.dob = new_dob_dt
                        match.person.dob_details = 0
                        dob_updated += 1

                addition_to_wiki = ""
                if match.matched_json.get("description"):
                    addition_to_wiki += "<p>{}</p>\n".format(
                        match.matched_json["description"]
                    )

                if match.matched_json.get("party"):
                    addition_to_wiki += "<p>На місцевих виборах у 2015 році балотувався від партії “{}“ до органу “{}”</p>\n".format(
                        match.matched_json["party"], match.matched_json["body"]
                    )

                if addition_to_wiki:
                    match.person.wiki_uk = (match.person.wiki_uk or "") +  "\n{}".format(addition_to_wiki)
                    wiki_updated += 1

                match.applied = True
                if options["real_run"]:
                    match.person.save()
                    match.save()

        self.stdout.write(
            "DOB mismatches: {}\nDOB updated: {}\nWiki updated: {}".format(
                dob_mismatch, dob_updated, wiki_updated
            )
        )
