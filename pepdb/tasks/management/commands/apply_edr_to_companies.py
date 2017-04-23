# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import Company
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

    def parse_address(self, location):
        chunks = list(
            map(unicode.strip, location.split(u",")))

        zip_code = chunks[0].strip()
        orig = location
        city = ""
        street = ""
        appt = ""

        try:
            if len(chunks) == 3:
                city = u", ".join([chunks[2], chunks[1]])

            else:
                if u"обл" in chunks[1].lower() or u"крим" in chunks[1].lower():
                    if u"район" in chunks[2].lower():
                        city = u", ".join([chunks[3], chunks[2], chunks[1]])

                        if len(chunks) > 4:
                            street = chunks[4]

                        if len(chunks) > 5:
                            appt = chunks[5]
                    else:
                        city = u", ".join([chunks[2], chunks[1]])
                        if u"район" in chunks[3]:
                            street = chunks[4]

                            if len(chunks) > 5:
                                appt = chunks[5]
                        else:
                            street = chunks[3]

                            if len(chunks) > 4:
                                appt = chunks[4]
                else:
                    city = chunks[1]
                    street = chunks[3]
                    if len(chunks) > 4:
                        appt = chunks[4]

            if not zip_code.isdigit():
                zip_code = ""

            # Sanity check
            if u"буд" in appt.lower() or appt == "" or appt.isdigit():
                return (zip_code, city, street, appt)
            else:
                self.stderr.write(
                    "Cannot parse %s, best results so far is %s" % (
                        location,
                        ", ".join([zip_code, city, street, appt])
                    )
                )

                return None
        except IndexError:
            self.stderr.write(
                "Cannot parse %s" % location
            )

            return None

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
                parsed = self.parse_address(r.location)

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

                    if company.edrpou and company.edrpou != r.edrpou:
                        self.stdout.write(
                            "Replacing edrpou %s with %s for company %s, %s" % (
                                company.edrpou,
                                r.edrpou,
                                company.name,
                                company.id
                            )
                        )

                    company.zip_code = zip_code
                    company.city = city
                    company.street = street
                    company.appt = appt
                    company.edrpou = r.edrpou
                else:
                    company.raw_address = r.location

                if options["real_run"]:
                    company.save()
