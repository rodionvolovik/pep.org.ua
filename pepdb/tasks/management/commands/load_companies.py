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
                    edrpou=row[u"Код_ЄДРПОУ"].lstrip("0"),
                    location=row[u"Місцезнаходження"],
                    company_profile=row[u"Основний_вид_діяльності"],
                    head=row[u"ПІБ_керівника"],
                    name=row[u"Найменування"],
                    short_name=row[u"Скорочена_назва"],
                    status=row[u"Стан"],
                ).to_dict(True))

                if len(portion) >= 10000:
                    bulk(es, portion)

                    self.stdout.write(
                        'Loaded {} registry companies to search index'.format(i + 1))

                    portion = []

            bulk(es, portion)