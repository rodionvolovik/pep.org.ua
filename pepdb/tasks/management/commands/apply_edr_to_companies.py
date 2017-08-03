# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import Company
from core.utils import parse_address
from tasks.elastic_models import EDRPOU
from tasks.models import CompanyMatching


class Command(BaseCommand):
    help = ('Takes finished tasks for companies matching and applies '
            'to the Company model')

    company_types = [
        u"зареєстровано",
        u"порушено справу про банкрутство",
        u"порушено справу про банкрутство (санація)",
        u"зареєстровано, свідоцтво про державну реєстрацію недійсне",
        u"в стані припинення",
        u"припинено",
    ]

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Apply registry matching results for real',
        )

    def handle(self, *args, **options):
        tasks = CompanyMatching.objects.exclude(
            edrpou_match="NONE").exclude(
            edrpou_match="").exclude(
            edrpou_match__isnull=True).filter(status="m")

        for t in tasks:
            try:
                company = Company.objects.get(pk=t.company_id)
            except Company.DoesNotExist:
                self.stderr.write(
                    "Cannot find company %s" % t.company_id
                )
                continue

            res = EDRPOU.search().query(
                "term", edrpou=t.edrpou_match.lstrip("0")).execute()

            res = sorted(
                res, key=lambda x: self.company_types.index(x.status))

            for r in res[:1]:
                parsed = parse_address(r.location)
                r.edrpou = r.edrpou.rjust(8, "0")

                if parsed:
                    skip = False
                    zip_code, city, street, appt = parsed

                    if company.zip_code and company.zip_code != zip_code:
                        self.stdout.write(
                            "NOT replacing zipcode %s with %s for company %s, %s" % (
                                company.zip_code,
                                zip_code,
                                company.name,
                                company.id
                            )
                        )
                        skip = True

                    if company.city and company.city != city:
                        self.stdout.write(
                            "NOT replacing city %s with %s for company %s, %s" % (
                                company.city,
                                city,
                                company.name,
                                company.id
                            )
                        )
                        skip = True

                    if company.street and company.street != street:
                        self.stdout.write(
                            "NOT replacing street %s with %s for company %s, %s" % (
                                company.street,
                                street,
                                company.name,
                                company.id
                            )
                        )
                        skip = True

                    if company.appt and company.appt != appt:
                        self.stdout.write(
                            "NOT replacing appt %s with %s for company %s, %s" % (
                                company.appt,
                                appt,
                                company.name,
                                company.id
                            )
                        )
                        skip = True

                    if skip:
                        self.stdout.write("=======\n\n")
                        continue

                    company.zip_code = zip_code
                    company.city = city
                    company.street = street
                    company.appt = appt
                else:
                    company.raw_address = r.location

                if company.edrpou and company.edrpou != r.edrpou:
                    self.stdout.write(
                        "Replacing edrpou %s with %s for company %s, %s" % (
                            company.edrpou,
                            r.edrpou,
                            company.name,
                            company.id
                        )
                    )

                company.edrpou = r.edrpou

                if options["real_run"]:
                    company.save()
