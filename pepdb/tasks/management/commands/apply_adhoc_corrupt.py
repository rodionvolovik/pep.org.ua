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
    help = "Add data from matches with database of corruption crimes to the PEP db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--real_run",
            default=False,
            action="store_true",
            help="Add matched data to wiki articles",
        )

    def handle(self, *args, **options):
        q = AdHocMatch.objects.filter(dataset_id="corrupt", applied=False, status="a")

        wiki_updated = 0
        activate(settings.LANGUAGE_CODE)

        with tqdm.tqdm(total=q.count()) as pbar:
            for match in q.select_related("person").nocache().iterator():
                pbar.update(1)

                if not match.person:
                    continue

                addition_to_wiki = "<p>{} {} притягувався до відповідальності за корупційне правопорушення, а саме за {}{} {}, деталі можна дізнатися в судовій справі № {}.</p>".format(
                    match.matched_json["FIO"],
                    match.matched_json["DATE_NAK_DST"],
                    match.matched_json["STAT"] ,
                    match.matched_json["SPOS_VCH_DP"],
                    match.matched_json["SKLAD_COR_PR"],
                    match.matched_json["NUM_NAK_DST"] or match.matched_json["NUM_SUD_R"],
                ).replace(" ,", ",").replace(",,", ",")

                match.person.wiki_uk = (match.person.wiki_uk or "") + "\n{}".format(
                    addition_to_wiki
                )
                wiki_updated += 1

                match.applied = True
                if options["real_run"]:
                    match.person.save()
                    match.save()

        self.stdout.write("Wiki updated: {}".format(wiki_updated))
