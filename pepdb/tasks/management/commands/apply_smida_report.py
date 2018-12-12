# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from collections import defaultdict

from tqdm import tqdm
from django.core.management.base import BaseCommand

from core.importers.company import CompanyImporter
from core.model.persons import Person
from core.model.connections import Person2Company, Person2Person
from core.universal_loggers import PythonLogger
from core.utils import parse_fullname
from tasks.elastic_models import EDRPOU
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
        updated_companies_total = 0
        failed_companies_total = 0

        company_importer = CompanyImporter(logger=PythonLogger("cli_commands"))

        smida_candidates = SMIDACandidate.objects.filter(status="a")

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            edrpou = candidate.smida_edrpou

            if companies_dict.get(edrpou):
                continue

            ans = EDRPOU.find_by_edrpou(candidate.smida_edrpou)

            if len(ans) > 1:
                self.stderr.write(
                    "Too many companies found by code {}, skipping".format(edrpou)
                )

                failed_companies_total += 1
                continue

            if not ans:
                self.stderr.write(
                    "No company found by code {}, skipping".format(edrpou)
                )

                failed_companies_total += 1
                continue

            company, created = company_importer.get_or_create_from_edr_record(
                ans[0].to_dict(),
                options["real_run"])

            if not company:
                self.stderr.write(
                    "Cannot create a company by code {}, for the rec {}, skipping".format(
                        edrpou,
                        candidate.pk
                    )
                )

                failed_companies_total += 1
                continue

            if created:
                created_companies_total += 1
                tqdm.write("Created company {}".format(company))
            else:
                updated_companies_total += 1
                tqdm.write("Updated company {}".format(company))

            companies_dict[edrpou] = company

        self.stdout.write("Finished import companies.")
        # endregion

        # region Persons and P2C
        self.stdout.write("Starting import Persons and Person2Company relations.")
        smida_candidates = SMIDACandidate.objects.filter(status="a",
                                                         smida_is_real_person=True)

        peps = self.all_peps_names()
        self.persons_dict = {}
        self.persons_stats = {"created_total": 0, "matched_resolved": 0, "matched_not_resolved": 0}
        p2c_links_total = 0
        self.smida_p2c = self.person_2_companies_relations()

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            person_name = candidate.smida_parsed_name

            # If can't tie person with company skip it to avoid duplicates
            if not any(edrpou in companies_dict for edrpou in self.smida_p2c[person_name]):
                tqdm.write("Skipped person: {} from processing as he not tied to any valid EDRPOU."
                           .format(person_name))
                continue

            is_pep = person_name.strip().lower() in peps

            person = self.persons_dict.get(person_name)
            if not person:
                person = self.create_person(person_name, is_pep, candidate.smida_yob,
                                            options["real_run"])

            if person:
                company = companies_dict.get(candidate.smida_edrpou)

                if not company:
                    continue

                relationship_type = SMIDA_POSITIONS_MAPPING.get("{} {}".format(
                        candidate.smida_position_class,
                        candidate.smida_position_body),
                    candidate.smida_position
                )

                try:
                    Person2Company.objects.get(from_person=person,
                                   to_company=company,
                                   relationship_type__icontains=relationship_type,
                                   is_employee=True)
                except Person2Company.DoesNotExist:
                    p2c = Person2Company(from_person=person,
                                         to_company=company,
                                         relationship_type=relationship_type,
                                         is_employee=True)

                    dat_obr = candidate.matched_json.get("DAT_OBR") or ""
                    if dat_obr:
                        p2c.date_established = dt_parse(dat_obr)

                    termin_obr = candidate.matched_json.get("TERM_OBR") or ""
                    if termin_obr:
                        self.try_set_p2p_date_finished(p2c, termin_obr)

                    p2c_links_total += 1
                    tqdm.write("Created P2C relation: id: {} ({}) <=> id: {} ({}) EST. {}, FIN. {}"
                               .format(person.id or "N/A",
                                       person_name,
                                       company.id or "N/A",
                                       company.name_uk,
                                       p2c.date_established or "N/A",
                                       p2c.date_finished or "N/A"))

                    if options["real_run"]:
                        p2c.save()

        self.stdout.write("Finished import Persons and Person2Company relations.")
        # endregion

        # region Create P2P connections
        p2p_links_total = 0
        heads = self.company_heads_mapping()

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            person_name = candidate.smida_parsed_name
            heads_of_company = heads.get(candidate.smida_edrpou) or []
            from_person = self.persons_dict.get(person_name)

            for head in heads_of_company:
                to_person = self.persons_dict.get(head)

                if from_person == to_person:
                    continue

                try:
                    Person2Person.objects.get(from_person=from_person,
                                  to_person=to_person,
                                  from_relationship_type="ділові зв'язки",
                                  to_relationship_type="ділові зв'язки")
                except Person2Person.DoesNotExist:
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
            "Updated existing companies: {}.\n"
            "Created new companies: {}.\n"
            "Failed create companies: {}.\n"
            "Created new persons: {}.\n"
            "Matched existing resolved: {}.\n"
            "Matched existing not resolved: {}.\n"
            "Created P2C links: {}.\n"
            "Created P2P links: {}."
            .format(updated_companies_total,
                    created_companies_total,
                    failed_companies_total,
                    self.persons_stats["created_total"],
                    self.persons_stats["matched_resolved"],
                    self.persons_stats["matched_not_resolved"],
                    p2c_links_total,
                    p2p_links_total)
        )

    def create_person(self, person_name, is_pep, yob, real_run=False):

        def create_new_person():
            person = Person(
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
                is_pep=is_pep,
                type_of_official=1 if is_pep else 4
            )

            if yob and yob > 1850:
                dob = dt_parse("{}-01-01".format(yob))
                person.dob = dob
                person.dob_details = 2

            if real_run:
                person.save()

            self.persons_dict[person_name] = person
            self.persons_stats["created_total"] += 1
            return person

        qs = Person.objects.all()

        last_name, first_name, patronymic, _ = parse_fullname(person_name)
        if not last_name or not first_name:
            tqdm.write("Can not split name: {}".format(person_name))
            return

        qs = qs.filter(last_name_uk__icontains=last_name,
                       first_name_uk__icontains=first_name)

        if patronymic:
            qs = qs.filter(patronymic_uk__icontains=patronymic)

        name_matches = qs.count()

        if name_matches == 0:
            tqdm.write("No matches for: {}. Person will be created"
                       .format(person_name))
            return create_new_person()

        for person in qs.iterator():
            edrpou_list = [edrpou.rjust(8, "0") for edrpou in self.smida_p2c[person_name]]
            p2c = Person2Company.objects.filter(from_person=person, to_company__edrpou__in=edrpou_list)
            if p2c.count():
                tqdm.write("Matched {} for name: {}. Found common P2C relation, marked as known person."
                           .format(person.full_name, person_name))
                self.persons_dict[person_name] = person
                self.persons_stats["matched_resolved"] += 1
                return person

        tqdm.write("Found matches for name: {}. Person with same name will be created."
                   .format(person_name))

        self.persons_stats["matched_not_resolved"] += 1
        return create_new_person()


    def company_heads_mapping(self):
        companies_heads_dict = defaultdict(list)

        # select distinct by ("smida_edrpou", "smida_parsed_name") as same person
        # may have more several records of Head position for same company
        company_heads = SMIDACandidate.objects.filter(status="a",
                                              smida_is_real_person=True,
                                              smida_position_class="h") \
            .values_list("smida_edrpou", "smida_parsed_name") \
            .distinct("smida_edrpou", "smida_parsed_name")

        for edrpou, person_name in company_heads:
            companies_heads_dict[edrpou].append(person_name)

        return companies_heads_dict

    def person_2_companies_relations(self):
        person_to_companies = defaultdict(set)

        p2c = SMIDACandidate.objects.filter(status="a",
                                            smida_is_real_person=True) \
            .values_list("smida_edrpou", "smida_parsed_name") \
            .distinct("smida_edrpou", "smida_parsed_name")

        for edrpou, person_name in p2c:
            person_to_companies[person_name].add(edrpou)

        return person_to_companies

    def all_peps_names(self):
        return [name.strip().lower() for name in SMIDACandidate.objects.filter(status="a",
                                                  smida_is_real_person=True,
                                                  smida_position_class="h")
                    .values_list("smida_parsed_name", flat=True)
                    .distinct("smida_parsed_name")]

    def try_set_p2p_date_finished(self, p2c, termin_obr):
        match = re.search(r'(\d{2}\.\d{2}\.\d{4})', termin_obr)
        if match and match.group(1):
            p2c.date_finished = dt_parse(match.group(1))

        elif p2c.date_established:
            # try to match by regex
            years = None
            match = re.search(r'(^\d$|^\d\D|\D\d р)', termin_obr)
            if match and match.group(1):
                years = filter(lambda x: x.isdigit() and x != "0", match.group(1))

            if not years:
                # try find in dictionary
                for k, v in DT_LENGTH_MAP.items():
                    if k in termin_obr:
                        years = v
                        break

            if years:
                dt = p2c.date_established
                p2c.date_finished = dt.replace(year=dt.year + int(years))

DT_LENGTH_MAP = {
    u'дин рiк': 1,
    u'один рiк': 1,
    u'два роки': 2,
    u'три роки': 3,
    u'3(три) роки': 3,
    u'чотири роки': 4,
    u'п\'ять рокiв': 5,
    u'п’ять рокiв': 5,
    u'п"ять рокiв': 5
}


SMIDA_POSITIONS_MAPPING = {
    u'h sc': u'Голова правління',
    u'd sc': u'Заступник голови правління',
    u'm sc': u'Член правління',
    u'a sc': u'Член правління',
    u'h wc': u'Голова наглядової ради',
    u'd wc': u'Заступник голови наглядової ради',
    u'm wc': u'Член наглядової ради',
    u's wc': u'Член наглядової ради',
    u'h ac': u'Голова ревізійної комісії',
    u'd ac': u'Член ревізійної комісії',
    u'm ac': u'Член ревізійної комісії',
    u'a a': u'Член правління',
    u'h h': u'Голова правління',
    u'd h': u'Заступник голови правління'
}
