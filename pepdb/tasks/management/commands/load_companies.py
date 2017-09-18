# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from codecs import open as enc_open

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from dateutil.parser import parse

from django.core.management.base import BaseCommand

from tasks.elastic_models import EDRPOU


class Command(BaseCommand):
    help = ('Loads XML with data from registry of companies of Ukraine into '
            'elastic index for further matching with companies in DB')

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            help='XML file with EDR export',
        )

        parser.add_argument(
            'date_of_export',
            help='Date when dataset was exported',
        )

    def iter_docs(self, s, import_date):
        mapping = {
            'NAME': 'name',
            'SHORT_NAME': 'short_name',
            'EDRPOU': 'edrpou',
            'ADDRESS': 'location',
            'BOSS': 'head',
            'KVED': 'company_profile',
            'STAN': 'status',
            'FOUNDERS': 'founders'
        }

        for i, chunk in enumerate(re.finditer('<RECORD>.*?</RECORD>', s)):
            company = {}
            founders_list = []
            try:
                etree = ET.fromstring(chunk.group(0))
            except ParseError:
                self.stderr.write('Cannot parse record #{}, {}'.format(i, chunk))
                continue

            for el in etree.getchildren():
                if el.tag == 'EDRPOU' and el.text and el.text.lstrip('0'):
                    company[mapping[el.tag]] = int(el.text)
                elif el.tag == 'FOUNDERS':
                    for founder in el.getchildren():
                        founders_list.append(founder.text)
                else:
                    company[mapping[el.tag]] = el.text

            company[mapping['FOUNDERS']] = founders_list
            company["last_update"] = import_date

            if i and i % 50000 == 0:
                self.stdout.write('Processed {} companies from XML feed'.format(i))

            yield EDRPOU(**company).to_dict(True)

    def handle(self, *args, **options):
        file_path = options['file_path']

        dt = parse(options["date_of_export"], dayfirst=True)

        Index(EDRPOU._doc_type.index).delete(ignore=404)
        EDRPOU.init()
        es = connections.get_connection()

        with enc_open(file_path, 'r', encoding='cp1251') as fp:
            bulk(es, self.iter_docs(fp.read().encode('utf-8'), import_date=dt), chunk_size=10000)
