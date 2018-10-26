# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict

from tqdm import tqdm

from django.db.models import Q
from django.core.management.base import BaseCommand

from core.model.companies import Company
from core.model.persons import Person
from core.model.connections import Person2Company
from tasks.models import SMIDACandidate
from dateutil.parser import parse as dt_parse
from core.utils import render_date
from django.utils.translation import activate
from django.conf import settings


class Command(BaseCommand):

    help = "Add data from matches with wikidata to the PEP db"

    wikimedia = "https://upload.wikimedia.org/wikipedia/commons/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--real_run",
            default=False,
            action="store_true",
            help="Add matched data to wiki articles",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting matching job ...")

        activate(settings.LANGUAGE_CODE)

        companies_created = 0

        #####################################
        ############ Companies ##############
        #####################################
        smida_candidates = SMIDACandidate.objects.filter(status="a")

        companies_dict = {}

        #for candidate in tqdm(smida_candidates.nocache().iterator(), total=smida_candidates.count()):
        for candidate in smida_candidates.nocache().iterator():

            edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")

            try:
                company = companies_dict.get(edrpou) or Company.objects.nocache().get(edrpou=edrpou)
            except Company.DoesNotExist:
                company = Company(
                    edrpou=edrpou,
                    name_uk=candidate.smida_company_name.strip()
                )
                self.stdout.write("Created company {}".format(company))
                companies_created += 1

                if options["real_run"]:
                    company.save()

            companies_dict[edrpou] = company


        self.stdout.write(
            "Companies created: {}".format(companies_created)
        )

        #####################################
        ############# Persons ###############
        #####################################

        smida_candidates = SMIDACandidate.objects.filter(status="a", smida_is_real_person=True)

        peps = self.all_peps_names()
        created_peps = {}

        associated = self.all_associated_names(peps)
        created_assoc = {}

        heads = self.company_heads_mapping()

        for candidate in smida_candidates.nocache().iterator():     # for candidate in tqdm(smida_candidates.nocache().iterator(), total=smida_candidates.count()):
            person_name = candidate.smida_parsed_name
            is_pep = person_name in peps

            # if not is_pep:
            #     continue

            person = created_peps.get(person_name) \
                  or created_assoc.get(person_name) \
                  or self.create_person(candidate, is_pep, created_peps, created_assoc, options["real_run"])

            edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")
            company = companies_dict.get(edrpou)

            if not company:
                self.stderr.write("Can not find a company: {}".format(edrpou))
                continue

            p2c = Person2Company(from_person=person,
                                 to_company=company,
                                 relationship_type=candidate.smida_position,
                                 is_employee=True, #??? Check this is correct
                                 )

            if options["real_run"]:
                p2c.save()

        # Second iteration to create associated persons
        for candidate in smida_candidates.nocache().iterator():
            person_name = candidate.smida_parsed_name
            is_pep = person_name in peps

            if is_pep:
                continue



        self.stdout.write(
            "New PEPs count: {}".format(len(created_peps))
        )

    def create_person(self, person_name, is_pep, created_peps, created_assoc, real_run=False):
        qs = Person.objects.all()

        for term in person_name.split():
            qs = qs.filter(Q(first_name_uk__icontains=term) |
                           Q(last_name_uk__icontains=term) |
                           Q(patronymic_uk__icontains=term))

        if qs.nocache().count() == 0:
            self.stdout.write("No matches for: {}. Person will be created".format(person_name))
            names = person_name.split()

            # Create new person
            person = Person(
                last_name=names[0],
                first_name=names[1],
                patronymic=names[2] if len(names) == 3 else "",
                is_pep=is_pep,
                type_of_official=1 if is_pep else 4
            )

            # self.apply_dob(candidate.smida_yob, person)

            if real_run:
                person.save()

            if is_pep:
                created_peps[person_name] = person
            else:
                created_assoc[person_name] = person

            return person, True
        return None, False

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

    def all_associated_names(self, peps):
        all_names = list(SMIDACandidate.objects.filter(status="a",
                                                  smida_is_real_person=True)
                    .values_list("smida_parsed_name", flat=True)
                    .distinct("smida_parsed_name"))
        return list(set(all_names) - set(peps))

    def apply_dob(self, yob, person):
        if yob and yob > 1850:
            dob = dt_parse("{}-01-01".format(yob))
            person.dob = dob
            person.dob_details = 2


            #edrpou = unicode(candidate.smida_edrpou).rjust(8, "0")
            # qs = Person.objects.all()
            #
            # for term in person_name.split():
            #     qs = qs.filter(Q(first_name_uk__icontains=term) |
            #                    Q(last_name_uk__icontains=term) |
            #                    Q(patronymic_uk__icontains=term))
            #
            # if qs.nocache().count() == 0:
            #     self.stdout.write("No matches for: {}. Person will be created".format(person_name))
            #     names = person_name.split()
            #
            #     # Create new person
            #     person = Person(
            #         last_name=names[0],
            #         first_name=names[1],
            #         patronymic=names[2] if len(names) == 3 else "",
            #         is_pep=is_pep,
            #         type_of_official=1 if is_pep else 4
            #     )
            #
            #     #self.apply_dob(candidate.smida_yob, person)
            #
            #     if options["real_run"]:
            #         person.save()
            #
            #     created_peps[person_name] = person
            #
            #     # Create person2company
            #
            #     break #TODO remove

            # elif len(persons) == 1:
            #     person = persons[0]
            #     matched_persons_count += 1
            #     matched_persons_keys.append(candidate.smida_parsed_name)
            #     self.stdout.write("Matched smida person: {} ==> {} {} {}.".format(
            #         candidate.smida_parsed_name,
            #         person.last_name, person.first_name, person.patronymic
            #     ))
            # else:
            #     pass