# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import xlsxwriter
from django.core.management.base import BaseCommand
from tasks.models import BeneficiariesMatching


class Command(BaseCommand):
    help = ('Exports the list of foreign companies from declarations of PEPs '
            'which aren\'t yet in DB to an excel file for further processing '
            'and reconciliation with the registry')

    def add_arguments(self, parser):
        parser.add_argument(
            'target_file',
            help='Excel file to export to',
        )

    def handle(self, *args, **options):
        keys = [
            "owner_name",
            "company_name_declaration",
            "company_name_en",
            "zip",
            "city",
            "street",
            "appt",
            "country",
            "company_code",
            "notes",
            "status",
            "company_name_orig",
            "link",
            "founder_1",
            "founder_2",
            "founder_3",
            "founder_4",
            "founder_5",
            "founder_6",
            "founder_7"
        ]

        workbook = xlsxwriter.Workbook(options["target_file"])
        for kind, name in (("f", "Founders"), ("b", "Beneficiaries")):
            ws = workbook.add_worksheet(name)

            for i, f in enumerate(keys):
                ws.write(0, i, f)

            row = 1
            for t in BeneficiariesMatching.objects.filter(
                    status="n", type_of_connection=kind):

                base_res = {
                    "owner_name": t.person_json["full_name"]
                }

                for company in t.pep_company_information:
                    res = base_res.copy()
                    res["company_name_declaration"] = company["company_name"]
                    res["company_name_en"] = company["en_name"] or ""
                    res["country"] = company["country"]
                    res["zip"] = company["address"] or ""
                    res["company_code"] = company["beneficial_owner_company_code"]

                    for i, f in enumerate(keys):
                        ws.write(row, i, res.get(f, ""))

                    row += 1

        workbook.close()
