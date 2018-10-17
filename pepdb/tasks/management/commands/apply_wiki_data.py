# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import tqdm
import jmespath
import hashlib
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from tasks.models import WikiMatch
from dateutil.parser import parse as dt_parse
from core.utils import render_date
from django.utils.translation import activate
from django.conf import settings


class Command(BaseCommand):

    help = "Add data from matches with wikidata to the PEP db"

    wikimedia = "https://upload.wikimedia.org/wikipedia/commons/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--real_run",
            default=False,
            action="store_true",
            help="Add matched data to wiki articles",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting matching job ...")

        path_dob = jmespath.compile("[0].claims.P569[0].mainsnak.datavalue.value")
        path_photo = jmespath.compile("[0].claims.P18[0].mainsnak.datavalue.value")
        path_uk_wiki = jmespath.compile("[0].sitelinks.ukwiki.url")
        path_en_wiki = jmespath.compile("[0].sitelinks.enwiki.url")
        path_ru_wiki = jmespath.compile("[0].sitelinks.ruwiki.url")

        self.dob_mismatch = 0
        self.dob_updated = 0
        self.photo_updated = 0

        activate(settings.LANGUAGE_CODE)

        wiki_matches = WikiMatch.objects.filter(status="a")

        with tqdm.tqdm(total=wiki_matches.count()) as pbar:

            for match in wiki_matches.select_related("person").nocache().iterator():
                pbar.update(1)
                wikidata = match.matched_json

                if not match.person:
                    continue

                self.current_match = match

                self.match_dob(path_dob.search(wikidata))

                self.match_photo(path_photo.search(wikidata), options["real_run"])

                self.match_links(path_uk_wiki.search(wikidata),
                                 path_en_wiki.search(wikidata),
                                 path_ru_wiki.search(wikidata))

                if options["real_run"]:
                    match.person.save()
                    match.save()

        self.stdout.write(
            "DOB mismatches: {}\nDOB updated: {}\nPhotos updated: {} ".format(
                self.dob_mismatch, self.dob_updated, self.photo_updated
            )
        )

    def match_links(self, uk_wiki_url, en_wiki_url, ru_wiki_url):

        pass



    def match_photo(self, wikidata_photo_name, save_photo=False):
        match = self.current_match

        person_photo = match.person.photo

        if person_photo or not wikidata_photo_name:
            return

        wikidata_photo_name = wikidata_photo_name.replace(" ", "_")
        md5 = hashlib.md5()
        md5.update(wikidata_photo_name.encode("utf-8"))
        hash = md5.hexdigest()

        a, b = tuple(hash[:2])
        photo_url = "{}{}/{}{}/{}".format(self.wikimedia, a, a, b, wikidata_photo_name)

        resp = requests.get(photo_url)

        if resp.status_code == 200:
            if save_photo:
                match.person.photo.save(
                    wikidata_photo_name,
                    ContentFile(resp.content))

            self.photo_updated += 1
        else:
            self.stdout.write("Can not download image {} for profile {}{}".format(
                photo_url,
                settings.SITE_URL,
                match.person.get_absolute_url()
            ))

        return

    def match_dob(self, wikidata_dob_obj):
        match = self.current_match
        person_dob = match.person.date_of_birth

        if not wikidata_dob_obj:
            return

        wikidata_dob = self.parse_wikidata_dob(wikidata_dob_obj)

        if not wikidata_dob:
            return

        if not person_dob:
            match.person.dob = wikidata_dob
            match.person.dob_details = 0
            self.dob_updated += 1
        else:
            new_dob = render_date(wikidata_dob, match.person.dob_details)

            if person_dob != new_dob:
                self.stderr.write(
                    "DOB mismatch for profile {}{}, current {}, new {}".format(
                        settings.SITE_URL,
                        match.person.get_absolute_url(),
                        person_dob,
                        render_date(wikidata_dob, 0)
                    )
                )
                self.dob_mismatch += 1
                return

            if match.person.dob_details > 0:
                match.person.dob = wikidata_dob
                match.person.dob_details = 0
                self.dob_updated += 1

    def parse_wikidata_dob(self, dob_obj):

        if dob_obj["precision"] == 11:
            return dt_parse(dob_obj["time"][1:])

        # if dob_obj["precision"] == 9:
        #     dob_obj["time"] = dob_obj["time"].replace("-00", "-01", 2)
        #     return (dt_parse(dob_obj["time"][1:]), 2)
