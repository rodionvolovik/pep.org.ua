# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
from datetime import date
from unicodecsv import reader
from django.core.management.base import BaseCommand
from core.models import Person, Person2Company, Company


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "infile",
            type=argparse.FileType("r"),
            help="CSV file with ids of existing MPs",
        )

    def handle(self, *args, **kwargs):
        qs = Person2Company.objects.select_related("from_person", "to_company").filter(
            from_person__publish=True,
            from_person__type_of_official=1,
            to_company_id=63,
            relationship_type_uk__istartswith="Народний депутат",
            date_finished__isnull=True,
            date_established__gte=date(2014, 11, 27),
            date_established__lte=date(2019, 8, 1),
        )

        for conn in qs.nocache().iterator():
            print(
                "Updating old connection for MP {} ({}), {}".format(
                    conn.from_person, conn.from_person_id, conn.relationship_type_uk
                )
            )
            conn.date_finished = date(2019, 8, 29)
            conn.date_finished_details = 0
            conn.date_confirmed = date(2019, 8, 29)
            conn.date_confirmed_details = 0
            conn.relationship_type_uk = "Народний депутат України VIIІ скликання"
            conn.relationship_type_en = (
                "Member of Parliament of Ukraine of the 8th Ukrainian Verkhovna Rada"
            )
            conn.save()

        qs = Person.objects.filter(publish=False)

        for person in qs.nocache().iterator():
            print(
                "Showing new {} {} ({})".format(
                    "MP" if person.type_of_official == 1 else "relative of MP",
                    person,
                    person.pk,
                )
            )
            person.publish = True
            person.save()

            if person.type_of_official == 1:
                for conn in Person2Company.objects.filter(
                    from_person=person, to_company_id=63
                ):
                    conn.date_established = date(2019, 8, 29)
                    conn.date_established_details = 0
                    conn.date_confirmed = date(2019, 8, 29)
                    conn.date_confirmed_details = 0

                    conn.relationship_type_uk = "Народний депутат України"
                    conn.relationship_type_en = "Member of Parliament of Ukraine"
                    conn.save()

        r = reader(kwargs["infile"])

        for l in r:
            p = Person.objects.get(pk=int(l[2]))
            print("Adding connection to Rada for {}".format(p))
            conn = Person2Company(
                from_person=p,
                to_company_id=63,
                date_established=date(2019, 8, 29),
                date_established_details=0,
                date_confirmed=date(2019, 8, 29),
                date_confirmed_details=0,
                is_employee=True,
                relationship_type_uk="Народний депутат України",
                relationship_type_en="Member of Parliament of Ukraine",
            )
            conn.save()