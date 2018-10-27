# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict

from tqdm import tqdm

from django.db.models import Q
from django.core.management.base import BaseCommand

from core.model.companies import Company
from core.model.persons import Person
from core.model.connections import Person2Company, Person2Person
from tasks.models import SMIDACandidate
from dateutil.parser import parse as dt_parse
from django.utils.translation import activate
from django.conf import settings


class Command(BaseCommand):

    help = "Add data from matches with wikidata to the PEP db"

    def add_arguments(self, parser):
        parser.add_argument(
            "--real_run",
            default=False,
            action="store_true",
            help="Save data to database",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting matching job ...")
        activate(settings.LANGUAGE_CODE)

        # region Companies
        self.stdout.write("Starting import Companies.")

        companies_dict = {}
        created_companies_total = 0
        matched_companies_total = 0

        smida_candidates = SMIDACandidate.objects.filter(status="a")

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")

            if companies_dict.get(edrpou):
                continue

            try:
                company = Company.objects.nocache().get(edrpou=edrpou)
                matched_companies_total += 1
            except Company.DoesNotExist:
                company = Company(
                    edrpou=edrpou,
                    name_uk=candidate.smida_company_name.strip()
                )
                tqdm.write("Created company {}".format(company))
                created_companies_total += 1

                if options["real_run"]:
                    company.save()

            companies_dict[edrpou] = company

        self.stdout.write("Finished import companies.")
        # endregion

        # region Persons and P2C
        self.stdout.write("Starting import Persons and Person2Company relations.")
        smida_candidates = SMIDACandidate.objects.filter(status="a",
                                                         smida_is_real_person=True)

        peps = self.all_peps_names()
        persons_dict = {}
        persons_created_total = 0
        p2c_links_total = 0

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            person_name = candidate.smida_parsed_name
            is_pep = person_name in peps

            person = persons_dict.get(person_name)
            if not person:
                person = self.create_person(person_name, is_pep,
                                            persons_dict, options["real_run"])
                if person:
                    persons_created_total += 1

            if person:
                edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")
                company = companies_dict.get(edrpou)

                p2c = Person2Company(from_person=person,
                                     to_company=company,
                                     relationship_type=candidate.smida_position,
                                     is_employee=True)

                p2c_links_total += 1
                tqdm.write("Created P2C relation: id: {} ({}) <=> id: {} ({})"
                           .format(person.id or "N/A",
                                   person_name,
                                   company.id or "N/A",
                                   company.name_uk))

                if options["real_run"]:
                    p2c.save()

        self.stdout.write("Finished import Persons and Person2Company relations.")
        # endregion

        # region Create P2P connections
        p2p_links_total = 0
        heads = self.company_heads_mapping()

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")
            person_name = candidate.smida_parsed_name

            heads_of_company = heads.get(edrpou) or []

            # it is likely that either from_person or to_person is None
            # as we skip processing names that was already have records in db
            from_person = persons_dict.get(person_name)
            if not from_person:
                tqdm.write("Can not create P2P. Candidate '{}' was not recognized"
                           " as unique person".format(person_name))
                continue

            for head in heads_of_company:
                to_person = persons_dict.get(head)

                if not to_person:
                    tqdm.write("Can not create P2P. Head '{}' was not recognized"
                               " as unique person".format(head))
                    continue

                if from_person == to_person:
                    continue

                p2p = Person2Person(from_person=from_person,
                                    to_person=to_person,
                                    from_relationship_type="ділові зв'язки",
                                    to_relationship_type="ділові зв'язки")

                tqdm.write("Created P2P relation: id: {} ({}) <=> id: {} ({})"
                           .format(from_person.id or "N/A",
                                   from_person.full_name,
                                   to_person.id or "N/A",
                                   to_person.full_name))
                p2p_links_total += 1

                if options["real_run"]:
                    p2p.save()

        self.stdout.write("Finished import Person2Person relations.")
        # endregion

        self.stdout.write(
            "Found existing companies: {}.\n"
            "Created new companies: {}.\n"
            "Created new persons: {}.\n"
            "Created P2C links: {}.\n"
            "Created P2P links: {}."
                .format(matched_companies_total,
                        created_companies_total,
                        persons_created_total,
                        p2c_links_total,
                        p2p_links_total)
        )

    def create_person(self, person_name, is_pep, created_persons, real_run=False):
        qs = Person.objects.all()

        names = [n.strip() for n in person_name.split()]
        if len(names) < 2:
            tqdm.write("Can not split name: {}".format(person_name))
            return

        qs = qs.filter(last_name_uk__icontains=names[0],
                       first_name_uk__icontains=names[1])

        if len(names) == 3:
            qs = qs.filter(patronymic_uk__icontains=names[2])

        name_matches = qs.nocache().count()

        # As we have not enough of proof that SmidaCandidate name matched
        # in storage is same person, he will be skipped from processing
        # in order to avoid creating duplicate objects

        if name_matches == 0:
            tqdm.write("No matches for: {}. Person will be created"
                       .format(person_name))

            # Create new person
            person = Person(
                last_name=names[0],
                first_name=names[1],
                patronymic=names[2] if len(names) == 3 else "",
                is_pep=is_pep,
                type_of_official=1 if is_pep else 4
            )

            # self.apply_dob(candidate.smida_yob, person) #TODO should it be applied?

            if real_run:
                person.save()

            created_persons[person_name] = person
            return person

        else:
            tqdm.write("Found {} {} for name: {}. Skip it from processing."
                       .format(name_matches,
                               "matches" if name_matches > 1 else "match",
                               person_name))

    def company_heads_mapping(self):
        companies_heads_dict = defaultdict(list)

        # select distinct by ("smida_edrpou", "smida_parsed_name") as same person
        # may have more several records of Head position for same company
        company_heads = SMIDACandidate.objects.filter(status="a",
                                              smida_is_real_person=True,
                                              smida_position_class="h") \
            .values_list("smida_edrpou", "smida_parsed_name") \
            .order_by("smida_edrpou", "smida_parsed_name") \
            .distinct("smida_edrpou", "smida_parsed_name")

        for edrpou, person_name in company_heads:
            edrpou = unicode(edrpou).rjust(8, "0")

            companies_heads_dict[edrpou].append(person_name)

        return companies_heads_dict

    def all_peps_names(self):
        return list(SMIDACandidate.objects.filter(status="a",
                                                  smida_is_real_person=True,
                                                  smida_position_class="h")
                    .values_list("smida_parsed_name", flat=True)
                    .distinct("smida_parsed_name"))

    def apply_dob(self, yob, person):
        if yob and yob > 1850:
            dob = dt_parse("{}-01-01".format(yob))
            person.dob = dob
            person.dob_details = 2
