# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from unicodecsv import DictReader

from tasks.elastic_models import EDRPOU


class Command(BaseCommand):
    help = ('Loads CSV with data from registry of companies of Ukraine into '
            'elastic index for further matching with companies in DB')

    args = '<file_path>'

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError(
                'First argument must be a CSV file with companies')

        Index(EDRPOU._doc_type.index).delete(ignore=404)
        EDRPOU.init()
        es = connections.get_connection()

        with open(file_path, "r") as fp:
            dr = DictReader(fp, encoding="utf-8")
            portion = []

            for i, row in enumerate(dr):
                portion.append(EDRPOU(
                    edrpou=row[u"EDRPOU"].lstrip("0"),
                    location=row[u"ADDRESS"],
                    company_profile=row[u"KVED"],
                    head=row[u"BOSS"],
                    name=row[u"NAME"],
                    short_name=row[u"SHORT_NAME"],
                    status=row[u"STAN"],
                ).to_dict(True))

                if len(portion) >= 50000:
                    bulk(es, portion)

                    self.stdout.write(
                        'Loaded {} registry companies to search index'.format(i + 1))

                    portion = []

            bulk(es, portion)
