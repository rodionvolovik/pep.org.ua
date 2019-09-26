# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

import json
import re
import argparse
import xml.etree.ElementTree as ET
from dateutil.parser import parse as dt_parse
from codecs import open
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

from core.importers.company import CompanyImporter
from core.universal_loggers import PythonLogger
from tasks.models import NAISCompany


class Command(BaseCommand):
    EXCLUDE_PATTERNS = (
        re.compile("РАЙОН", flags=re.I),
        re.compile("ДЕРЖАВНОЇ АДМ[iіIІ]Н[iіIІ]СТРАЦ[iіIІ]Ї", flags=re.I),
        re.compile("ЄДНАНЕ УПРАВЛ[iіIІ]ННЯ ПЕНС[iіIІ]ЙНОГО ФОНДУ УКРАЇНИ", flags=re.I),
        re.compile("М[iіIІ]СЬКИЙ"),
        re.compile("У М\.", flags=re.I),
        re.compile("У М[iіIІ]СТ[iіIІ]", flags=re.I),
        re.compile("ДЕРЖАВНОГО КАЗНАЧЕЙСТВА", flags=re.I),
        re.compile("М[iіIІ]СЬКОЇ РАДИ", flags=re.I),
        re.compile("СЕЛИЩНОЇ РАДИ", flags=re.I),
        re.compile("РАЙДЕРЖАДМ[iіIІ]Н[iіIІ]СТРАЦ[iіIІ]Ї", flags=re.I),
        re.compile("м[iіIІ]ста", flags=re.I),
        re.compile("РЕСПУБЛ[iіIІ]Ц[iіIІ] КРИМ", flags=re.I),
        re.compile("РЕСПУБЛ[iіIІ]КИ КРИМ", flags=re.I),
        re.compile("АРХ[iіIІ]В", flags=re.I),
        re.compile("М[iіIІ]СТА", flags=re.I),
        re.compile("В[iіIІ]ДД[iіIІ]Л", flags=re.I),
        re.compile("ТЕРИТОР[iіIІ]АЛЬНОГО УПРАВЛ[iіIІ]ННЯ ЮСТИЦ[iіIІ]Ї", flags=re.I),
        re.compile("ДЕРЖАВНА НОТАР[iіIІ]АЛЬНА", flags=re.I),
        re.compile("ПОЛ[iіIІ]Ц[iіIІ]Ї ОХОРОНИ", flags=re.I),
        re.compile("ОКРУЖНИЙ СУД", flags=re.I),
        re.compile("ОБЛДЕРЖАДМ[iіIІ]Н[iіIІ]СТРАЦ[iіIІ]Ї", flags=re.I),
    )

    def add_arguments(self, parser):
        # parser.add_argument(
        #     "--real_run",
        #     action="store_true",
        #     dest="real_run",
        #     default=False,
        #     help="Create and update companies",
        # )

        parser.add_argument(
            "--set_flag",
            choices=[
                "public_office",
                "political_party",
                "state_enterprise",
                "affiliated_with_pep",
                "bank",
                "service_provider",
            ],
            help="Set flag for the company",
        )

        parser.add_argument("infile", help="File with data to import")

    def __init__(self):
        self.company_info = {}

    def _iter_xml(self, fp):
        mapping = {
            "Організаційно-правова_форма": "form",
            "Найменування": "name",
            "Скорочена_назва": "short_name",
            "Код_ЄДРПОУ": "edrpou",
            "Стан": "status",
            "ADDRESS": "location",
            "CHARTER_CAPITAL": "charter_capital",
            "Дата_державної_реэстрації": "founded",
            "Керівник": "head",
        }

        try:
            content = fp.read()
        except:
            content = ""

            with tqdm() as pbar:
                while True:
                    chunk = fp.read(1024 * 1024 * 10)
                    if not chunk:
                        break
                    content += chunk
                    pbar.update(len(chunk))

        regex = "<DATA_RECORD>.*?</DATA_RECORD>"

        for chunk in tqdm(re.finditer(regex, content, flags=re.S | re.U)):
            company = {}
            founders_list = []

            try:
                etree = ET.fromstring(
                    chunk.group(0)
                    .replace("Місцезнаходження", "ADDRESS")
                    .replace("Статутний_капітал,_грн.", "CHARTER_CAPITAL")
                    .replace("Засновник/кінцевий_бенефіціар", "FOUNDER")
                    .replace("Код_ЄДРПОУ_засн/бенефіц", "FOUNDER_CODE")
                    .replace("Частка_в_стат._капіталі,_грн.", "SHARE")
                    .encode("utf-8")
                )
            except Exception as e:
                print("Error parsing {}, exception was {}".format(chunk.group(0), e))

            edrpou = None
            for el in etree.getchildren():
                if el.tag not in mapping:
                    continue
                field = mapping[el.tag]
                if field == "edrpou":
                    if el.text and el.text.lstrip("0"):
                        company[field] = int(el.text)
                        edrpou = int(el.text)
                    else:
                        company[field] = 0
                elif field == "founded" and el.text:
                    company[field] = dt_parse(el.text, yearfirst=True).date()
                else:
                    if field:
                        company[field] = el.text

            if edrpou is not None:
                if edrpou not in self.company_info:
                    self.company_info[edrpou] = company
                    yield company

    def handle(self, *args, **kwargs):
        activate(settings.LANGUAGE_CODE)

        logger = PythonLogger("cli_commands")
        self.importer = CompanyImporter(logger=logger)

        filter_statuses = [
            "припинено",
            "ліквідація",
            "розпорядження майном",
            "зареєстровано, свідоцтво про державну реєстрацію недійсне",
        ]

        if kwargs["set_flag"] == "public_office":
            filter_statuses.append("в стані припинення")

        with open(kwargs["infile"], encoding="cp1251") as fp:
            for company_rec in self._iter_xml(fp):
                company, created = self.importer.get_or_create_from_edr_record(
                    company_rec, save=False
                )

                if created:
                    if company_rec["status"].lower() in filter_statuses:
                        continue

                    if kwargs["set_flag"] == "public_office":
                        if any(
                            map(
                                lambda x: x.search(company_rec["name"])
                                or x.search(company_rec.get("short_name", "")),
                                self.EXCLUDE_PATTERNS,
                            )
                        ):
                            logger.warning(
                                "Skipping company {} with edrpou {} and status {}".format(
                                    company_rec["name"],
                                    company_rec["edrpou"],
                                    company_rec["status"],
                                )
                            )

                            continue

                    logger.warning(
                        "New company {} with edrpou {} added and status {} created".format(
                            company_rec["name"],
                            company_rec["edrpou"],
                            company_rec["status"],
                        )
                    )

                edrpou = int(company_rec["edrpou"])
                if NAISCompany.objects.filter(pk=edrpou).exclude(status="p").count():
                    logger.warning(
                        "Task for company {} with edrpou {} was already processed".format(
                            company_rec["name"], company_rec["edrpou"]
                        )
                    )
                    continue

                task, _ = NAISCompany.objects.update_or_create(
                    pk=edrpou,
                    defaults={
                        "status": "p",
                        "created": created,
                        "matched_json": company_rec,
                        "company_name": company_rec.get("short_name", company_rec["name"]),
                        "company_status": company_rec["status"],
                        "company_type": kwargs["set_flag"],
                    },
                )
