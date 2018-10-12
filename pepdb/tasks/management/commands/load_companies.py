# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import codecs
from random import randrange
import requests
import os.path
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import logging
from time import sleep
from io import TextIOWrapper, open
from unicodecsv import DictReader
from zipfile import ZipFile
from cStringIO import StringIO

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from dateutil.parser import parse


from tasks.elastic_models import EDRPOU


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reader")


class EDR_Reader(object):
    """
    Simple reader class which allows to iterate over Zipped/not Zipped XML/CSV file
    """

    def __init__(self, in_file, timestamp, revision, file_type="zip"):
        """
        Initializes EDR_Reader class

        :param in_file: file object (zipped or not)
        :type in_file: StringIO or file handler
        :param timestamp: date of export of the file
        :type timestamp: datetime
        :param revision: revision of the dump
        :type revision: string
        :param file_type: type of the file (usually extension)
        :type file_type: string
        """

        self.file = in_file
        self.file_type = file_type
        self.timestamp = timestamp
        self.revision = revision

    def iter_docs(self):
        """
        Reads input file record by record.

        :returns: iterator over company records from registry
        :rtype: collections.Iterable[dict]
        """

        if self.file_type == "zip":
            with ZipFile(self.file) as zip_arch:
                for fname in zip_arch.namelist():
                    try:
                        dec_fname = unicode(fname)
                    except UnicodeDecodeError:
                        dec_fname = fname.decode("cp866")

                    if "uo" in dec_fname.lower() or "юо" in dec_fname.lower():
                        logger.info("Reading {} file from archive {}".format(dec_fname, self.file))

                        if dec_fname.lower().endswith(".xml"):
                            with zip_arch.open(fname, 'r') as fp_raw:
                                for l in self._iter_xml(fp_raw):
                                    yield EDRPOU(**l).to_dict(True)

                        if dec_fname.lower().endswith(".csv"):
                            with zip_arch.open(fname, 'r') as fp_raw:
                                for l in self._iter_csv(fp_raw):
                                    yield EDRPOU(**l).to_dict(True)
        elif self.file_type == "xml":
            for l in self._iter_xml(self.file):
                yield EDRPOU(**l).to_dict(True)

        elif self.file_type == "csv":
            for l in self._iter_csv(self.file):
                yield EDRPOU(**l).to_dict(True)

    def _iter_xml(self, fp_raw):
        """
        Regex magic is required to
        cover records that was incorrectly exported and incomplete, thus
        make whole XML file invalid (happens sometime)
        """

        with TextIOWrapper(fp_raw, encoding="cp1251") as fp:
            mapping = {
                'NAME': 'name',
                'SHORT_NAME': 'short_name',
                'EDRPOU': 'edrpou',
                'ADDRESS': 'location',
                'BOSS': 'head',
                'KVED': 'company_profile',
                'STAN': 'status',
                'FOUNDERS': 'founders',

                "Найменування": 'name',
                "Скорочена_назва": 'short_name',
                "Код_ЄДРПОУ": 'edrpou',
                "Місцезнаходження": 'location',
                "ПІБ_керівника": 'head',
                "Основний_вид_діяльності": 'company_profile',
                "Стан": 'status',
                "C0": ""
            }

            content = fp.read()
            if "RECORD" in content[:1000]:
                regex = '<RECORD>.*?</RECORD>'
            else:
                regex = '<ROW>.*?</ROW>'

            for i, chunk in enumerate(re.finditer(regex, content, flags=re.S | re.U)):
                company = {}
                founders_list = []
                try:
                    # Fucking ET!
                    etree = ET.fromstring(chunk.group(0).replace("Місцезнаходження", "ADDRESS").encode("utf-8"))
                except ParseError:
                    logger.error('Cannot parse record #{}, {}'.format(i, chunk))
                    continue

                for el in etree.getchildren():
                    if el.tag == 'EDRPOU' and el.text and el.text.lstrip('0'):
                        company[mapping[el.tag]] = int(el.text)
                    elif el.tag == 'FOUNDERS':
                        for founder in el.getchildren():
                            founders_list.append(founder.text)
                    else:
                        if mapping[el.tag]:
                            company[mapping[el.tag]] = el.text

                company[mapping['FOUNDERS']] = founders_list
                company["last_update"] = self.timestamp
                company["file_revision"] = self.revision

                if i and i % 50000 == 0:
                    logger.warning('Read {} companies from XML feed'.format(i))

                yield company

    def _iter_csv(self, fp_raw):
        r = DictReader(fp_raw, delimiter=str(";"), encoding="cp1251")

        mapping = {
            "Найменування": 'name',
            "Скорочена назва": 'short_name',
            "Код ЄДРПОУ": 'edrpou',
            "Місцезнаходження": 'location',
            "ПІБ керівника": 'head',
            "Основний вид діяльності": 'company_profile',
            "Стан": 'status',
        }

        for i, chunk in enumerate(r):
            company = {}

            for k, v in chunk.items():
                if k.strip():
                    if mapping[k] == "edrpou" and v:
                        company[mapping[k]] = int(v)
                    else:
                        company[mapping[k]] = v

            company['founders'] = []
            company["last_update"] = self.timestamp
            company["file_revision"] = self.revision

            if i and i % 50000 == 0:
                logger.warning('Read {} companies from CSV feed'.format(i))

            yield company


class Command(BaseCommand):
    help = ('Loads XML with data from registry of companies of Ukraine into '
            'elastic index for further matching with companies in DB')

    def add_arguments(self, parser):
        parser.add_argument(
            '--revision',
            help='EDR dump revision to retrieve (leave empty to retrieve latest)',
        )

        parser.add_argument(
            '--guid',
            default="73cfe78e-89ef-4f06-b3ab-eb5f16aea237",
            help='Dataset to retrieve',
        )

        parser.add_argument(
            '--filename',
            help='Filename of the dump to load file manually',
        )

        parser.add_argument(
            '--dump_date',
            help='Date of dump, obtained manually, day first',
        )

    def handle(self, *args, **options):
        self.proxies = {}
        if hasattr(settings, "PROXY"):
            self.proxies["http"] = settings.PROXY
            self.proxies["https"] = settings.PROXY

        GUID = options["guid"]
        fp = None

        if not options["filename"]:
            try:
                if not options["revision"]:
                    response = requests.get(
                        "http://data.gov.ua/view-dataset/dataset.json",
                        {"dataset-id": GUID, "nocache": randrange(100)},
                        proxies=self.proxies
                    ).json()
                    timestamp = parse(response["changed"], dayfirst=True)
                else:
                    listing = requests.get(
                        "http://data.gov.ua/view-dataset/dataset.json",
                        {"dataset-id": GUID, "nocache": randrange(100)},
                        proxies=self.proxies
                    ).json()

                    for rev in listing["revisions"]:
                        if rev["revision_id"] == options["revision"]:
                            timestamp = parse(rev["created"], dayfirst=True)
                            break

                    sleep(0.2)
                    response = requests.get(
                        "http://data.gov.ua/view-dataset/dataset.json",
                        {"dataset-id": GUID, "revision-id": options["revision"], "nocache": randrange(100)},
                        proxies=self.proxies
                    ).json()

                files_list = response["files"]
                revision = response["revision_id"]
            except (TypeError, IndexError, KeyError):
                self.stderr.write("Cannot obtain information about dump file")
                raise

            if len(files_list) != 1:
                self.stderr.write("Too many files in API response, trying to find a proper one")
                for f in files_list:
                    if "uo" in f["url"].lower():
                        files_list = [f]
                        break
                else:
                    self.stderr.write("Nothing suitable found")
                    return

            dump = files_list[0]
            _, ext = os.path.splitext(dump["url"])

            r = requests.get(dump["url"], stream=True)
            reader = EDR_Reader(StringIO(r.content), timestamp, revision, ext.lower().lstrip("."))
        elif options["revision"] and options["dump_date"]:
            dump_date = timezone.make_aware(parse(options["dump_date"], dayfirst=True))
            _, ext = os.path.splitext(options["filename"])

            fp = open(options["filename"], "rb")
            reader = EDR_Reader(fp, dump_date, options["revision"], ext.lower().lstrip("."))
        else:
            self.stderr.write("You should provide (possibly fake) revision id and date of dump when loading files manually")

        Index(EDRPOU._doc_type.index).delete(ignore=404)
        EDRPOU.init()
        es = connections.get_connection()

        bulk(es, reader.iter_docs(), chunk_size=10000)

        if fp:
            fp.close()
