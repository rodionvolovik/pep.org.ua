# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from string import capwords
from dateutil import parser
from unicodecsv import DictReader

from django.db import migrations


def title(s):
    chunks = s.split()
    chunks = map(lambda x: capwords(x, u"-"), chunks)
    return u" ".join(chunks)


def parse_date(s):
    return parser.parse(s, default=datetime(1970, 1, 1)).date()


def load_peps(apps, schema_editor):
    Company = apps.get_model("core", "Company")
    Person = apps.get_model("core", "Person")

    with open("core/dicts/peps.csv", "r") as fp:
        r = DictReader(fp, errors="ignore")

        for l in r:
            company_ipn = l.get("ІПН", "")
            company_name = l.get("Назва", "")

            company = None

            if not company_ipn and not company_name:
                continue

            # Search by IPN first (if it's present)
            if company_ipn:
                try:
                    company = Company.objects.get(edrpou=company_ipn)
                except Company.DoesNotExist:
                    pass

            # then search by name (if it's present)
            if company_name:
                if company is None:
                    try:
                        company = Company.objects.get(
                            name=company_name)
                    except Company.DoesNotExist:
                        pass

            if company is None:
                company = Company(state_company=True)

            # Set missing params
            if not company.name:
                company.name = company_name

            if not company.edrpou:
                company.edrpou = company_ipn

            company.save()

            person_name = l.get("ПІБ", "")
            person_dob = l.get("Дата народження", "").strip()

            person_from = l.get("Дата призначення", "").strip()
            person_to = l.get("Дата звільнення", "").strip()

            if person_name:
                chunks = person_name.split(" ")
                if len(chunks) == 2:
                    last_name = title(chunks[0])
                    first_name = title(chunks[1])
                else:
                    last_name = title(" ".join(chunks[:-2]))
                    first_name = title(chunks[-2])
                    patronymic = title(chunks[-1])

                # Kind of get_or_create
                try:
                    person = Person.objects.get(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                        patronymic__iexact=patronymic
                    )
                except Person.DoesNotExist:
                    person = Person(
                        first_name=first_name,
                        last_name=last_name,
                        patronymic=patronymic
                    )

                person.is_pep = True
                person.type_of_official = 1
                if person_dob:
                    person.dob = parse_date(person_dob)

                person.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150311_0306'),
    ]

    operations = [
        migrations.RunPython(load_peps),
    ]
