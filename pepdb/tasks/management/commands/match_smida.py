# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import json
from time import sleep
from collections import defaultdict
from xml.etree import ElementTree
from hashlib import sha1
import argparse

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, now
from django.conf import settings

import requests
from requests.exceptions import RequestException
from unicodecsv import DictReader, reader
import tqdm
from elasticsearch_dsl import Q
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as dt_parse

from core.models import Person, Company
from core.utils import is_eng
from tasks.models import SMIDACandidate



class Command(BaseCommand):
    help = (
        "Search PEP comanies in SMIDA 5+% dataset and retrieving their reports from API"
        " to create key persons as pep or related persons"
    )

    CLASS_MARKERS = {
        re.compile(r"голова", flags=re.I | re.U): "h",
        re.compile(r"бухгалтер", flags=re.I | re.U): "a",
        re.compile(r"заступник", flags=re.I | re.U): "d",
        re.compile(r"голови", flags=re.I | re.U): "h",
        re.compile(r"член", flags=re.I | re.U): "m",
        re.compile(r"секретар", flags=re.I | re.U): "s",
    }

    BODY_MARKERS = {
        re.compile(r"правл[iі]н", flags=re.I | re.U): "sc",
        re.compile(r"р[еіi]?в[iі]з", flags=re.I | re.U): "ac",
        re.compile(r"бухгалтер", flags=re.I | re.U): "a",
        re.compile(r"нагляд", flags=re.I | re.U): "wc",
        re.compile(r"спостережної", flags=re.I | re.U): "wc",
        re.compile(r"нглядов", flags=re.I | re.U): "wc",
        re.compile(r"наг\.\s?ради", flags=re.I | re.U): "wc",
        re.compile(r"нагядово", flags=re.I | re.U): "wc",
        re.compile(r"корпоративний секретар", flags=re.I | re.U): "s",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "smida_file", type=argparse.FileType("r"), help="CSV with SMIDA 5% report"
        )

    def get_doc_hash(self, doc):
        return sha1(
            json.dumps(
                {
                    k: (doc.get(k) or "").lower().replace(" ", "")
                    for k in sorted(doc.keys())
                }
            )
        ).hexdigest()

    def handle(self, *args, **options):
        bodies_mapping = {kls: c for c, kls in SMIDACandidate.POSITION_BODIES}
        classes_mapping = {kls: c for c, kls in SMIDACandidate.POSITION_CLASSES}

        with open("core/dicts/smida_positions_mapping.csv", "r") as fp:
            r = reader(fp)

            positions_mapping = {}
            for pos in r:
                if not pos:
                    continue

                positions_mapping[pos[1].lower().strip()] = {
                    "class": classes_mapping[pos[3]],
                    "body": bodies_mapping[pos[2]]
                }

        r = DictReader(options["smida_file"])

        created_candidates = 0
        updated_candidates = 0
        ignored_candidates = 0
        smida_records = defaultdict(list)
        smida_owner_records = defaultdict(list)
        smida_indirect_records = defaultdict(list)

        for l in r:
            l["share"] = float(l["share"].replace(",", "."))
            smida_records[l["EDRPOU"].strip().lstrip("0")].append(l)
            smida_owner_records[l["owner_edrpou"].strip().lstrip("0")].append(l)

        pep_state_companies = set()
        for c in Company.objects.filter(state_company=True).nocache().iterator():
            edrpou = c.edrpou.lstrip("0")
            if edrpou:
                pep_state_companies.add(edrpou)

        matched_companies = {}

        for c in pep_state_companies:
            if c in smida_records:
                matched_companies[c] = {
                    "level": 0,
                    "shares": 100,
                    "name": smida_records[c][0]["emitent_name"],
                }

            if c in smida_owner_records:
                for l in smida_owner_records[c]:
                    edrpou = l["EDRPOU"].strip().lstrip("0")
                    if edrpou in matched_companies:
                        if matched_companies[edrpou]["level"] > 0:
                            matched_companies[edrpou]["shares"] += l["share"]
                    else:
                        matched_companies[edrpou] = {
                            "level": 1,
                            "shares": l["share"],
                            "name": l["emitent_name"],
                        }

        for i, c in enumerate(tqdm.tqdm(matched_companies)):
            if matched_companies[c]["shares"] <= 50:
                continue

            response = requests.get(
                "https://stockmarket.gov.ua/api/v1/issuer-report-index.xml",
                params={"edrpou": c.rjust(8, "0")},
            )

            tree = ElementTree.fromstring(response.content)

            for report in tree.findall(
                ".//{http://stockmarket.gov.ua/api/v1/report-index.xsd}item/[@href]"
            ):
                start_date = make_aware(dt_parse(
                    report.find(".//{http://stockmarket.gov.ua/api/v1/report-index.xsd}param[@name='STD']").text
                ))
                finish_date = make_aware(dt_parse(
                    report.find(".//{http://stockmarket.gov.ua/api/v1/report-index.xsd}param[@name='FID']").text
                ))

                try:
                    subresp = requests.get(
                        "https://stockmarket.gov.ua/api/v1/{}".format(
                            report.attrib["href"]
                        )
                    )

                    try:
                        subtree = ElementTree.fromstring(subresp.content)
                    except ElementTree.ParseError as e:
                        self.stderr.write(
                            "Skipping report {} as malformed".format(report.attrib["href"])
                        )
                        continue

                    report_dt = make_aware(dt_parse(subtree.attrib["timestamp"]))

                    for report_item in subtree.findall(
                        ".//{http://stockmarket.gov.ua/api/v1/report.xsd}table[@id='DTSPERSON_P']/{http://stockmarket.gov.ua/api/v1/report.xsd}row"
                    ):
                        position = report_item.find(
                            ".//{http://stockmarket.gov.ua/api/v1/report.xsd}param[@name='POSADA']"
                        )
                        full_name = report_item.find(
                            ".//{http://stockmarket.gov.ua/api/v1/report.xsd}param[@name='P_I_B']"
                        )
                        prev_position = report_item.find(
                            ".//{http://stockmarket.gov.ua/api/v1/report.xsd}param[@name='PO_POSAD']"
                        )
                        yob = report_item.find(
                            ".//{http://stockmarket.gov.ua/api/v1/report.xsd}param[@name='RIK']"
                        )

                        if position.text is None:
                            continue

                        # Some sane defaults
                        smida_position_body = "o"
                        smida_position_class = "o"

                        if position is not None:
                            if position.text.lower().strip() in positions_mapping:
                                smida_position_body = positions_mapping[position.text.lower().strip()]["body"]
                                smida_position_class = positions_mapping[position.text.lower().strip()]["class"]
                            else:
                                for rx, bm in self.BODY_MARKERS.items():
                                    if rx.search(position.text):
                                        smida_position_body = bm
                                        break

                                for rx, cm in self.CLASS_MARKERS.items():
                                    if rx.search(position.text):
                                        smida_position_class = cm
                                        break

                        if smida_position_class == "o" or smida_position_body == "o":
                            self.stdout.write(
                                "Position: {} {} {}".format(
                                    position.text,
                                    smida_position_class,
                                    smida_position_body,
                                )
                            )

                        parsed_name = ""
                        if full_name is None:
                            continue

                        parsed_chunks = []

                        if full_name.text is None:
                            continue

                        # TODO: better word splitting
                        for chunk in full_name.text.split():
                            # TODO: better detection of latin
                            chunk = (
                                chunk.replace("i", "і")
                                .replace("I", "І")
                                .replace("o", "о")
                                .replace("O", "О")
                            )
                            if (
                                is_eng(chunk)
                                or chunk.startswith("(")
                                or chunk.endswith(")")
                                or chunk in "-"
                                or chunk.startswith("-")
                            ):
                                break
                            elif chunk:
                                parsed_chunks.append(chunk)

                        smida_is_real_person = len(parsed_chunks) in [2, 3]

                        matched_json = {}
                        for param in report_item.findall(
                            ".//{http://stockmarket.gov.ua/api/v1/report.xsd}param"
                        ):
                            matched_json[param.attrib["name"]] = param.text

                        matched_json_hash = self.get_doc_hash(
                            {
                                "yob": yob.text if yob is not None else "",
                                "full_name": full_name.text
                                if full_name is not None
                                else "",
                                "position": position.text
                                if position is not None
                                else "",
                                "edrpou": c.rjust(8, "0"),
                            }
                        )

                        try:
                            person = SMIDACandidate.objects.get(matched_json_hash=matched_json_hash)

                            if not person.dt_of_first_entry or start_date < person.dt_of_first_entry:
                                person.dt_of_first_entry = start_date

                            if not person.dt_of_last_entry or finish_date > person.dt_of_last_entry:
                                person.dt_of_last_entry = finish_date

                            person.save()

                            if report_dt > person.smida_dt:
                                updated_candidates += 1
                                person.smida_edrpou = c
                                person.smida_level = matched_companies[c]["level"]
                                person.smida_shares = matched_companies[c]["shares"]
                                smida_company_name = matched_companies[c]["name"]
                                person.smida_name = full_name.text
                                person.smida_parsed_name = (
                                    " ".join(parsed_chunks) if smida_is_real_person else ""
                                )
                                person.smida_dt = report_dt
                                person.smida_position = (
                                    position.text if position is not None else ""
                                )
                                person.smida_prev_position = (
                                    prev_position.text or ""
                                    if prev_position is not None
                                    else "",
                                )
                                person.smida_yob = yob.text if yob is not None else ""
                                person.smida_is_real_person = smida_is_real_person
                                person.smida_position_body = smida_position_body
                                person.smida_position_class = smida_position_class
                                person.matched_json = matched_json
                                person.matched_json_hash = matched_json_hash
                                person.save()
                            else:
                                ignored_candidates += 1
                        except SMIDACandidate.DoesNotExist:
                            if report_dt + relativedelta(years=3) >= now():
                                person = SMIDACandidate.objects.create(
                                    **{
                                        "smida_edrpou": c,
                                        "smida_level": matched_companies[c]["level"],
                                        "smida_shares": matched_companies[c]["shares"],
                                        "smida_name": full_name.text,
                                        "smida_company_name": matched_companies[c]["name"],
                                        "smida_parsed_name": " ".join(parsed_chunks)
                                        if smida_is_real_person
                                        else "",
                                        "smida_dt": report_dt,
                                        "smida_position": position.text
                                        if position is not None
                                        else "",
                                        "smida_prev_position": prev_position.text or ""
                                        if prev_position is not None
                                        else "",
                                        "smida_yob": yob.text if yob is not None else "",
                                        "smida_is_real_person": smida_is_real_person,
                                        "smida_position_body": smida_position_body,
                                        "smida_position_class": smida_position_class,
                                        "matched_json": matched_json,
                                        "matched_json_hash": matched_json_hash,
                                        "dt_of_first_entry": start_date,
                                        "dt_of_last_entry": finish_date,
                                    }
                                )
                                created_candidates += 1
                except KeyError:
                    self.stderr.write("Cannot find a key in {}".format(report))

        self.stdout.write(
            "Candidates created: {}, candidates updated {}, candidates ignored {}".format(
                created_candidates, updated_candidates, ignored_candidates
            )
        )
