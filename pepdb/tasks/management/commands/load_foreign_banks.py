# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db.models import Q

from unicodecsv import DictReader
from core.models import Company, Country, Company2Country


class Command(BaseCommand):
    help = ('Imports foreign banks from csv file to DB')

    def add_arguments(self, parser):
        parser.add_argument(
            'input_file',
            help='CSV file to import from',
        )

    def handle(self, *args, **options):
        with open(options["input_file"], "r") as fp:
            r = DictReader(fp)

            for l in r:
                try:
                    country = Country.objects.get(
                        Q(name_en__iexact=l["country"].strip()) |
                        Q(name_uk__iexact=l["country"].strip()))
                except Country.DoesNotExist:
                    self.stderr.write("Cannot find country %s" % l["country"])
                    continue

                try:
                    bank, created = Company.objects.get_or_create(
                        name_en=l["name"].strip(),
                        defaults={
                            "name_uk": l["name"].strip(),
                            "zip_code": l["zip_code"].strip(),
                            "city_en": l["city"].strip(),
                            "street_en": l["street"].strip(),
                            "appt_en": l["appt"].strip(),
                            "city_uk": l["city"].strip(),
                            "street_uk": l["street"].strip(),
                            "appt_uk": l["appt"].strip(),
                            "edrpou": l["code"].strip()
                        }
                    )

                    if not created:
                        if not bank.edrpou and l["code"].strip():
                            bank.edrpou = l["code"].strip()
                            bank.save()

                    Company2Country.objects.get_or_create(
                        from_company=bank,
                        to_country=country,
                        relationship_type="registered_in"
                    )
                except Company.MultipleObjectsReturned:
                    self.stderr.write("Cannot find country %s" % l["country"])
                    continue
