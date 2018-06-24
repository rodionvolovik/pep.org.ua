# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings

from core.models import Declaration, Person, Company
from core.importers.company import CompanyImporter
from core.importers.person2company import Person2CompanyImporter
from core.universal_loggers import PythonLogger

from tasks.elastic_models import EDRPOU
from tasks.models import BeneficiariesMatching


class Command(BaseCommand):
    help = """

    """
    status_order = (
        "зареєстровано",
        "зареєстровано, свідоцтво про державну реєстрацію недійсне",
        "порушено справу про банкрутство",
        "порушено справу про банкрутство (санація)",
        "в стані припинення",
        "припинено",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Connect beneficiar owners to companies for real',
        )

    def get_latest_declaration_record(self, ownership):
        def key_fun(rec):
            return rec["year_declared"], rec.get("is_fixed", False)

        if ownership.pep_company_information:
            return sorted(
                ownership.pep_company_information,
                key=key_fun, reverse=True
            )[0]

    def connect_domestic_companies(self, save_it):
        for ownership in BeneficiariesMatching.objects.filter(status="m"):
            k = ownership.edrpou_match.lstrip("0")

            if k == "NONE":
                continue

            if not k:
                self.stderr.write(
                    "Approved company with the key %s has no edrpou!, skipping" %
                    (
                        ownership.company_key,
                    )
                )

                self.failed += 1
                continue

            ans = EDRPOU.find_by_edrpou(k)

            if len(ans) > 1:
                self.stderr.write(
                    "Too many companies found by code %s, for the key %s, skipping" %
                    (
                        ownership.edrpou_match,
                        ownership.company_key
                    )
                )

                self.failed += 1
                continue

            if not ans:
                try:
                    company = Company.objects.get(
                        edrpou=unicode(ownership.edrpou_match).rjust(8, "0"))
                except Company.DoesNotExist:
                    self.stderr.write(
                        "Cannot find a company by code %s, for the key %s, skipping" %
                        (
                            ownership.edrpou_match,
                            ownership.company_key
                        )
                    )

                    self.failed += 1
                    continue
            else:
                company, created = self.importer.get_or_create_from_edr_record(ans[0].to_dict(), save_it)

                if not company:
                    self.stderr.write(
                        "Cannot create a company by code %s, for the key %s, skipping" %
                        (
                            ownership.edrpou_match,
                            ownership.company_key
                        )
                    )

                    self.failed += 1
                    continue

                if created:
                    self.companies_created += 1
                    self.stdout.write("Created company %s" % company)
                else:
                    self.companies_updated += 1
                    self.stdout.write("Updated company %s" % company)

            try:
                person = Person.objects.get(pk=ownership.person)
            except Person.DoesNotExist:
                self.stderr.write(
                    "Cannot find a person by code %s, for the key %s, skipping" %
                    (
                        ownership.person,
                        ownership.company_key
                    )
                )
                self.failed += 1
                continue

            most_recent_record = self.get_latest_declaration_record(ownership)
            for d in ownership.declarations:
                try:
                    decl = Declaration.objects.get(pk=d)
                except Declaration.DoesNotExist:
                    self.stderr.write(
                        "Cannot find a declaration by id %s, for the key %s, skipping" %
                        (
                            d,
                            ownership.company_key
                        )
                    )
                    continue

                conn, conn_created = self.conn_importer.get_or_create_from_declaration(
                    person, company,
                    most_recent_record.get("link_type", "Бенефіціарний власник"), decl, save_it)

                if most_recent_record.get("percent_of_cost"):
                    conn.share = most_recent_record["percent_of_cost"]

                    if save_it:
                        conn.save()

                if conn_created:
                    self.connections_created += 1
                    self.stdout.write("Created connection %s" % conn)
                else:
                    self.connections_updated += 1
                    self.stdout.write("Updated connection %s" % conn)

            self.successful += 1

    def connect_foreign_companies(self, save_it):
        for ownership in BeneficiariesMatching.objects.filter(status="y"):
            if len(ownership.candidates_json) != 1:
                self.stderr.write(
                    "Strange number of matches (%s) for foreign company %s" %
                    (
                        len(ownership.candidates_json),
                        ownership.company_key
                    )
                )
                continue

            try:
                company = Company.objects.get(pk=ownership.candidates_json[0]["id"])
            except Company.DoesNotExist:
                self.stderr.write(
                    "Cannot find a company by id %s, for the key %s, skipping" %
                    (
                        ownership.candidates_json[0]["id"],
                        ownership.company_key
                    )
                )

                self.failed += 1
                continue

            try:
                person = Person.objects.get(pk=ownership.person)
            except Person.DoesNotExist:
                self.stderr.write(
                    "Cannot find a person by code %s, for the key %s, skipping" %
                    (
                        ownership.person,
                        ownership.company_key
                    )
                )
                self.failed += 1
                continue

            most_recent_record = self.get_latest_declaration_record(ownership)
            for d in ownership.declarations:
                try:
                    decl = Declaration.objects.get(pk=d)
                except Declaration.DoesNotExist:
                    self.stderr.write(
                        "Cannot find a declaration by id %s, for the key %s, skipping" %
                        (
                            d,
                            ownership.company_key
                        )
                    )
                    continue

                conn, conn_created = self.conn_importer.get_or_create_from_declaration(
                    person, company,
                    most_recent_record.get("link_type", "Бенефіціарний власник"), decl, save_it)

                if most_recent_record.get("percent_of_cost"):
                    conn.share = most_recent_record["percent_of_cost"]

                    if save_it:
                        conn.save()

                if conn_created:
                    self.connections_created += 1
                    self.stdout.write("Created connection %s" % conn)
                else:
                    self.connections_updated += 1
                    self.stdout.write("Updated connection %s" % conn)

            self.successful += 1

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)

        self.importer = CompanyImporter(logger=PythonLogger("cli_commands"))
        self.conn_importer = Person2CompanyImporter(logger=PythonLogger("cli_commands"))

        self.successful = 0
        self.failed = 0
        self.companies_created = 0
        self.companies_updated = 0
        self.connections_created = 0
        self.connections_updated = 0

        self.connect_domestic_companies(options["real_run"])
        self.connect_foreign_companies(options["real_run"])

        self.stdout.write(
            "Creation failed: %s, creation successful: %s" % (self.failed, self.successful)
        )
        self.stdout.write(
            "Companies created: %s, companies updated: %s" %
            (self.companies_created, self.companies_updated)
        )
        self.stdout.write(
            "Connections created: %s, connections updated: %s" %
            (self.connections_created, self.connections_updated)
        )
