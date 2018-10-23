# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tqdm import tqdm
from django.core.management.base import BaseCommand

from core.model.companies import Company
from core.model.persons import Person
from tasks.models import SMIDACandidate
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

        activate(settings.LANGUAGE_CODE)

        companies_created = 0
        companies_updated = 0

        smida_candidates = SMIDACandidate.objects.filter(status="a")

        companies_created_dict = {}

        #for candidate in tqdm(smida_candidates.nocache().iterator(), total=smida_candidates.count()):
        for candidate in smida_candidates.nocache().iterator():

            edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")

            try:
                company = companies_created_dict.get(edrpou) or Company.objects.get(edrpou=edrpou)
            except Company.DoesNotExist:
                company = Company(
                    edrpou=edrpou,
                    name_uk=candidate.smida_company_name.strip()
                )
                self.stdout.write("Created company {}".format(company))
                companies_created += 1
                companies_created_dict[edrpou] = company

                if options["real_run"]:
                    company.save()


        self.stdout.write(
            "Companies created: {}, companies updated: {}".format(companies_created, companies_updated)
        )
