# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings

import jmespath
from dateutil.parser import parse as dt_parse

from core.importers.company import CompanyImporter
from core.importers.person2company import Person2CompanyImporter
from core.universal_loggers import PythonLogger
from core.models import Person, Company, Person2Company
from tasks.elastic_models import EDRPOU
from tasks.models import AdHocMatch


class Command(BaseCommand):
    help = """
    Create and update connections to the companies using data from SMIDA
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Connect smida stakeholders to companies for real',
        )

    def handle(self, *args, **options):
        company_code_path = jmespath.compile("nacp_orig.step_7.*.emitent_ua_company_code")
        save_it = options["real_run"]
        activate(settings.LANGUAGE_CODE)

        self.importer = CompanyImporter(logger=PythonLogger("cli_commands"))
        self.conn_importer = Person2CompanyImporter(logger=PythonLogger("cli_commands"))

        successful = 0
        failed = 0
        total = 0
        companies_created = 0
        companies_updated = 0
        connections_created = 0
        connections_updated = 0

        for rec in AdHocMatch.objects.filter(
                status="a", dataset_id="smida_10").prefetch_related("person").nocache():

            total += 1
            if "EDRPOU" not in rec.matched_json:
                self.stderr.write("Approved company {} has no edrpou!, skipping".format(rec.pk))

                failed += 1
                continue

            if rec.person is None:
                self.stderr.write(
                    "Cannot find a person rec {}, skipping".format(rec.pk)
                )
                failed += 1
                continue

            ans = EDRPOU.find_by_edrpou(rec.matched_json["EDRPOU"])

            if len(ans) > 1:
                self.stderr.write(
                    "Too many companies found by code {}, skipping".format(rec.matched_json["EDRPOU"])
                )

                failed += 1
                continue

            if not ans:
                self.stderr.write(
                    "No company found by code {}, skipping".format(rec.matched_json["EDRPOU"])
                )

                failed += 1
                continue

            company, created = self.importer.get_or_create_from_edr_record(ans[0].to_dict(), save_it)

            if not company:
                self.stderr.write(
                    "Cannot create a company by code {}, for the rec {}, skipping".format(
                        rec.matched_json["EDRPOU"],
                        rec.pk
                    )
                )

                failed += 1
                continue

            if created:
                companies_created += 1
                self.stdout.write("Created company {}".format(company))
            else:
                companies_updated += 1
                self.stdout.write("Updated company {}".format(company))

            existing_connections = Person2Company.objects.filter(
                from_person=rec.person, to_company=company
            ).exclude(relationship_type_uk="Акціонер")

            if existing_connections:
                for ex_conn in existing_connections:
                    self.stderr.write("Connection between {} and {} already exists but has type {}".format(
                        ex_conn.from_person, ex_conn.to_company, ex_conn.relationship_type
                    ))

            conn, conn_created = self.conn_importer.get_or_create(
                rec.person, company,
                "Акціонер",
                rec.last_updated_from_dataset.date(),
                "https://smida.gov.ua/db/emitent/{}".format(rec.matched_json["EDRPOU"]),
                "За інформацією Агентства з розвитку інфраструктури фондового ринку України (АРІФРУ)",
                "According to the information Stock market infrastructure development agency of Ukraine (SMIDA)",
                save_it
            )
            if conn_created:
                connections_created += 1
            else:
                connections_updated += 1

            if "share" in rec.matched_json:
                conn.share = float(rec.matched_json["share"].replace(",", ".").strip())
                if save_it:
                    conn.save()

            decls = rec.person.get_declarations()
            if decls:
                decl = decls[0]
                if decl.nacp_declaration:
                    declared_companies = company_code_path.search(decl.source) or []
                    declared_companies = list(filter(None, set(map(lambda x: x.lstrip("0"), declared_companies))))
                    if rec.matched_json["EDRPOU"].lstrip("0") not in declared_companies:
                        self.stderr.write("Cannot find company {} ({}) in declaration {} of {}".format(
                            company, company.edrpou, decl.url, rec.person
                        ))
                else:
                    self.stderr.write("No declaration found for person {}".format(rec.person))                    


        self.stdout.write(
            "{} records processed, failed: {}, successed: {}".format(total, failed, successful)
        )

        self.stdout.write(
            "Companies created: {}, companies updated: {}".format(companies_created, companies_updated)
        )

        self.stdout.write(
            "Connections created: {}, connections updated: {}".format(connections_created, connections_updated)
        )
