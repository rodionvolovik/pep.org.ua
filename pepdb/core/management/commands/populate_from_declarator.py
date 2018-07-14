# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import argparse
from collections import defaultdict

from django.db.transaction import rollback, set_autocommit, commit

from dateutil.parser import parse as dt_parse
from tqdm import tqdm

try:
    import ijson.backends.yajl2_cffi as ijson
except ImportError:
    import ijson

from django.core.management.base import BaseCommand
from django.conf import settings

from core.models import Person, Company, Declaration, Person2Company, RelationshipProof


class Command(BaseCommand):
    help = "Populate persons and companies, load declarations from declarator dump (RU)"
    org_mapping = {
        "Совет Федерации": "Совет Федерации Федерального Собрания",
        "Правительство РФ": "Правительство Российской Федерации",
        "Администрация Президента РФ": "Администрация президента Российской Федерации",
    }

    def __init__(self, *args, **kwargs):
        # Accumulator for the career information
        self.careers = defaultdict(lambda: defaultdict(dict))
        self.persons = {}
        self.companies = {}
        return super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "declarator_dump", type=argparse.FileType("r"), help="Declarator dump"
        )

        parser.add_argument(
            "--offices",
            nargs="+",
            type=int,
            help="Office ids to use",
            default=[14, 5, 456, 453],
        )

        parser.add_argument(
            "--real_run",
            help="Store results to db or just perform a dry run",
            action="store_true",
            default=False,
        )

    def process_declaration(self, d):
        decl_office = d["main"]["office"]["name"]
        pep_office = self.org_mapping.get(decl_office, decl_office)

        office, office_created = Company.objects.get_or_create(
            name_uk=pep_office, defaults={"state_company": True, "legal_entity": True}
        )

        self.companies[office.pk] = office
        if office_created:
            self.stdout.write("Office {} created in db".format(office))

        person = Person.objects.filter(declarator_id=d["main"]["person"]["id"]).first()

        if not person:
            person = Person.objects.filter(
                last_name__iexact=d["main"]["person"]["family_name"],
                first_name__iexact=d["main"]["person"]["given_name"],
                patronymic__iexact=d["main"]["person"]["patronymic_name"],
            ).first()

            if person:
                last_workplace = person.last_workplace or {}
                self.stdout.write(
                    "Person {} that has position {} in declaration already found in db with position {} @ {}".format(
                        person,
                        d["main"]["office"]["post"],
                        last_workplace.get("company"),
                        last_workplace.get("position"),
                    )
                )
                person.is_pep = True
                person.type_of_official = 1
                person.declarator_id = d["main"]["person"]["id"]
                person.save()

        if not person:
            person = Person(
                last_name=d["main"]["person"]["family_name"],
                first_name=d["main"]["person"]["given_name"],
                patronymic=d["main"]["person"]["patronymic_name"],
                is_pep=True,
                type_of_official=1,
                declarator_id=d["main"]["person"]["id"],
            )

            person.save()
            self.stdout.write("Created person {}".format(person))

        self.persons[person.pk] = person

        decl_id = "{}_{}_{}_{}".format(
            d["main"]["person"]["id"],
            d["main"]["office"]["id"],
            d["main"]["document_type"]["id"],
            d["main"]["year"],
        )

        decl, decl_created = Declaration.objects.get_or_create(
            declaration_id=decl_id,
            defaults={
                "last_name": d["main"]["person"]["family_name"],
                "first_name": d["main"]["person"]["given_name"],
                "patronymic": d["main"]["person"]["patronymic_name"],
                "position": d["main"]["office"]["post"][:512],
                "office": d["main"]["office"]["name"],
                "region": d["main"]["office"]["type"]["name"],
                "year": d["main"]["year"],
                "source": d,
                "url": "https://declarator.org/",  # WTF?
                "confirmed": "a",
                "fuzziness": 0,
                "person": person,
                "nacp_declaration": False,
                "declarator_declaration": True,
                "relatives_populated": True,
                "to_link": True,
                "to_watch": False,
                "acknowledged": True,
                "batch_number": 1,
            },
        )

        if decl_created:
            self.stdout.write("Created declaration {}".format(decl))

        self.careers[person.pk][office.pk][d["main"]["year"]] = (decl.pk, decl.position)

    def position_key(self, pos):
        return (
            pos.lower()
            .replace(" ", "")
            .replace("государственнойдумы", "гд")
            .replace("российскойфедерации", "рф")
        )

    def handle(self, *args, **options):
        # Rough number for now just to have nice progressbar
        with tqdm(total=113738) as pbar:
            set_autocommit(False)
            for item in ijson.items(options["declarator_dump"], "item"):
                pbar.update(1)
                if item["main"]["office"]["id"] in options["offices"]:
                    self.process_declaration(item)

            for person_id, offices in self.careers.items():
                person = self.persons[person_id]
                for office_id, career_path in offices.items():
                    office = self.companies[office_id]
                    years = list(career_path.keys())
                    positions = list(career_path.values())

                    if not all(
                        self.position_key(positions[0][1]) == self.position_key(p[1])
                        for p in positions
                    ):
                        self.stdout.write("\n" + "=" * 80)
                        self.stdout.write(
                            "Person {} has strange and bizzare career at office {}".format(
                                person, office
                            )
                        )
                        for year in sorted(years):
                            self.stdout.write(
                                "{}: {}".format(year, career_path[year][1])
                            )
                        self.stdout.write("=" * 80)

                    elif len(years) != (max(years) - min(years) + 1):
                        self.stdout.write("\n" + "=" * 80)
                        self.stdout.write(
                            "Person {} has gaps in his career at office {}".format(
                                person, office
                            )
                        )
                        for year in sorted(years):
                            self.stdout.write(
                                "{}: {}".format(year, career_path[year][1])
                            )
                        self.stdout.write("=" * 80)

            if not options["real_run"]:
                rollback()
            else:
                commit()
            set_autocommit(True)
