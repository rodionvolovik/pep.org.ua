# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from collections import defaultdict
from unicodecsv import DictReader

from core.model.exc import CannotResolveRelativeException
from core.models import Company, Declaration
from core.importers.person2company import Person2CompanyImporter
from core.universal_loggers import PythonLogger


class Command(BaseCommand):
    def find_bank(self, edrpou, name):
        if edrpou:
            if edrpou in self.edrpous_mapping:
                return [self.banks_dict[
                    self.edrpous_mapping[self.edrpous_mapping[edrpou]]
                ]]

        if name in self.names_mapping:
            return [
                self.banks_dict[code]
                for code in self.names_mapping[name]
            ]

        stripped_name = name.strip('"\'')
        if stripped_name in self.names_mapping:
            return [
                self.banks_dict[code]
                for code in self.names_mapping[stripped_name]
            ]

        if name in self.names_only_mapping:
            try:
                company = Company.objects.get(
                    name_en__iexact=self.names_only_mapping[name])
                return [company]
            except Company.DoesNotExist:
                self.stderr.write(
                    "Cannot find company %s (%s) in db by name" % (
                        name, edrpou)
                )

        self.stderr.write(
            "Cannot find bank %s (%s) in mapping" % (name, edrpou)
        )

        return None

    def add_arguments(self, parser):
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Connect persons to banks for real',
        )

    def handle(self, *args, **options):
        self.banks_dict = {}
        self.edrpous_mapping = {}
        self.names_only_mapping = {}
        self.names_mapping = defaultdict(set)
        importer = Person2CompanyImporter(
            logger=PythonLogger("cli_commands"))

        # Reading mapping between edrpous of bank branches and
        # edrpou of main branch of the bank
        with open("core/dicts/bank_edrpous_mapping.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                self.edrpous_mapping[bank["edrpou_branch"]] = bank["edrpou_base"]

        # Reading mapping between names of bank from declaration and
        # their real names (foreign banks that has no edrpou)
        with open("core/dicts/foreign_banks_mapping.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                self.names_only_mapping[bank["name"]] = bank["real_name"]
                self.names_only_mapping[bank["name"].strip('"\'')] = bank["real_name"]

        # Reading mapping between names of bank and it's edrpous
        with open("core/dicts/bank_names_mapping.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                self.names_mapping[bank["name"]].add(bank["edrpou"])
                self.names_mapping[bank["name"].strip('"\'')].add(bank["edrpou"])

        with open("core/dicts/true_banks.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                if bank["edrpou"]:
                    edrpou = bank["edrpou"]
                    try:
                        self.banks_dict[edrpou] = Company.objects.get(
                            edrpou=edrpou.rjust(8, "0"))
                    except Company.DoesNotExist:
                        self.stderr.write(
                            "Cannot find bank with edrpou %s" % edrpou)
                else:
                    self.stderr.write("Bank %s has no edrpou" % bank["name"])

        successful = 0
        failed = 0
        created_records = 0
        updated_records = 0
        for d in Declaration.objects.filter(
                nacp_declaration=True, confirmed="a"):
            data = d.source["nacp_orig"]

            if isinstance(data.get("step_12"), dict):
                for cash_rec in data["step_12"].values():
                    if not isinstance(cash_rec, dict):
                        continue

                    rec_type = cash_rec.get("objectType", "").lower()
                    person = d.person

                    if rec_type != "кошти, розміщені на банківських рахунках":
                        continue

                    if cash_rec.get("person", "1") != "1":
                        try:
                            person, _ = d.resolve_person(
                                cash_rec.get("person"))
                        except CannotResolveRelativeException as e:
                            self.stderr.write(unicode(e))
                            continue

                    bank_name = cash_rec.get(
                        "organization_ua_company_name") or \
                        cash_rec.get("organization_ukr_company_name", "")
                    bank_name = bank_name.lower().strip()

                    bank_edrpou = cash_rec.get(
                        "organization_ua_company_code", "")
                    bank_edrpou = bank_edrpou.lstrip("0").strip()

                    if bank_name or bank_edrpou:
                        bank_matches = self.find_bank(bank_edrpou, bank_name)
                        if bank_matches is None:
                            failed += 1
                            continue

                        for bank in bank_matches:
                            conn, created = importer.get_or_create_from_declaration(
                                person, bank, "Клієнт", d)

                            if created:
                                created_records += 1
                            else:
                                updated_records += 1

                            if options["real_run"]:
                                conn.save()

                        successful += 1

        self.stdout.write(
            "Mapping failed: %s, mapping successful: %s" % (failed, successful)
        )
        self.stdout.write(
            "Connections created: %s, connections updated: %s" %
            (created_records, updated_records)
        )
