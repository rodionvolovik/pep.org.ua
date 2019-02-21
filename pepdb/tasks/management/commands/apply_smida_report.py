# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from datetime import date, datetime, timedelta
from collections import defaultdict

from django.db.models import Count, Max
from tqdm import tqdm
from django.core.management.base import BaseCommand

from core.importers.company import CompanyImporter
from core.model.persons import Person
from core.model.connections import Person2Company, Person2Person
from core.universal_loggers import PythonLogger
from core.utils import parse_fullname, title
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
        pep_heads = self.company_heads_mapping()

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

            if created and edrpou in pep_heads:
                company.state_company = True
                if options["real_run"]:
                    company.save()

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
                tqdm.write("Created {} {}".format("state company" if company.state_company else "company", company))
            else:
                updated_companies_total += 1
                tqdm.write("Updated company {}".format(company))

            companies_dict[edrpou] = company

        self.stdout.write("Finished import companies.")
        # endregion

        # region Persons and P2C
        self.stdout.write("Starting import Persons and Person2Company relations.")
        smida_candidates = SMIDACandidate.objects.filter(status="a",
                                                         smida_is_real_person=True)\
                                                 .order_by("dt_of_first_entry")

        peps = self.all_peps_names()
        self.persons_dict = {}
        self.new_persons_pk = []
        self.persons_stats = {"created_total": 0, "matched_resolved": 0, "matched_not_resolved": 0}
        p2c_links_created = 0
        p2c_links_updated = 0
        self.smida_p2c = self.person_2_companies_relations()
        self.last_reports = self.get_companies_last_report()

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            person_name = candidate.smida_parsed_name.strip().lower()

            # If can't tie person with company skip it to avoid duplicates
            if not any(edrpou in companies_dict for edrpou in self.smida_p2c[person_name]):
                tqdm.write("Skipped person: {} from processing as he not tied to any valid EDRPOU."
                           .format(person_name))
                continue

            is_pep = person_name in peps

            person = self.persons_dict.get(person_name)
            if not person:
                person = self.create_person(person_name, is_pep, candidate.smida_yob,
                                            options["real_run"])
            # The same person might have been created from a record without smida_yob
            else:
                self.update_person_dob(person, candidate.smida_yob, real_run=options["real_run"])

            if person:
                company = companies_dict.get(candidate.smida_edrpou)

                if not company:
                    continue

                pb_key = "{} {}".format(candidate.smida_position_class, candidate.smida_position_body)
                relationship_type = SMIDA_POSITIONS_MAPPING.get(pb_key)

                if not relationship_type:
                    relationship_type = candidate.smida_position
                    tqdm.write("Relation missing from a mapping for SMIDACandidate ID: {}"
                               .format(candidate.id))

                # Calc date finished
                date_finished = self.p2c_get_date_finished(candidate)
                df_calculated = False
                if not date_finished and candidate.dt_of_last_entry:
                    company_last_report = self.last_reports.get(candidate.smida_edrpou)

                    if company_last_report and person_name not in company_last_report['persons'] \
                            and company_last_report['date'].date() > candidate.dt_of_last_entry.date():
                        date_finished = candidate.dt_of_last_entry
                        df_calculated = True

                # Calc date established
                de_calculated = False
                date_established = self.p2c_get_date_established(candidate)
                if not date_established:
                    if not date_finished or candidate.dt_of_first_entry.date() < date_finished.date():
                        date_established = candidate.dt_of_first_entry
                        de_calculated = True

                if date_established:
                    # update previous position on this work
                    prev_position = Person2Company.objects \
                        .filter(from_person=person, to_company=company,
                                is_employee=True, date_established__lt=date_established) \
                        .exclude(relationship_type__icontains=relationship_type)\
                        .order_by("-date_established").first()

                    if prev_position:
                        if de_calculated:
                            prev_position.date_finished = date_established - timedelta(days=1)
                        else:
                            prev_position.date_finished = date_established
                        prev_position.date_finished_details = 0

                        if options["real_run"]:
                            prev_position.save()

                        tqdm.write("Updated previous position for SMIDACandidate ID: {}"
                                   .format(candidate.id))

                # Get or create p2c
                try:
                    p2c = Person2Company.objects.get(from_person=person,
                                   to_company=company,
                                   relationship_type__icontains=relationship_type,
                                   is_employee=True)
                    updated = False

                    if date_finished:
                        old_val = p2c.date_finished
                        if self.update_p2c_date_finished(p2c, date_finished, df_calculated):
                            tqdm.write("Updated date_finished for P2C relation with id: {} Old: {}, New: {}"
                                       .format(p2c.id, old_val, date_finished))
                            updated = True

                    if date_established:
                        old_val = p2c.date_established
                        if self.update_p2c_date_established(p2c, date_established):
                            tqdm.write("Updated date_established for P2C relation with id: {} Old: {}, New: {}"
                                       .format(p2c.id, old_val, date_established))
                            updated = True

                    if updated:
                        p2c.date_confirmed = candidate.dt_of_last_entry or datetime.now()

                    p2c_links_updated += int(updated)

                    if options["real_run"]:
                        p2c.save()

                except Person2Company.DoesNotExist:
                    p2c = Person2Company(from_person=person,
                                         to_company=company,
                                         relationship_type=relationship_type,
                                         is_employee=True,
                                         date_established=date_established,
                                         date_finished=date_finished,
                                         date_confirmed=candidate.dt_of_last_entry or datetime.now())

                    p2c_links_created += 1
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
        self.stdout.write("New persons having multiple companies related")
        self.new_persons_having_multiple_company_relations()

        # region Create P2P connections

        smida_candidates = SMIDACandidate.objects.filter(status="a",
                                                         smida_is_real_person=True) \
            .order_by("dt_of_last_entry")

        p2p_links_total = 0

        for candidate in tqdm(smida_candidates.nocache().iterator(),
                              total=smida_candidates.count()):
            person_name = candidate.smida_parsed_name.strip().lower()
            heads_of_company = pep_heads.get(candidate.smida_edrpou) or []
            from_person = self.persons_dict.get(person_name)

            for head in heads_of_company:
                to_person = self.persons_dict.get(head)

                if from_person == to_person:
                    continue

                try:
                    p2p = Person2Person.objects.get(from_person=from_person,
                                  to_person=to_person,
                                  from_relationship_type="ділові зв'язки",
                                  to_relationship_type="ділові зв'язки")

                    p2p.date_confirmed = candidate.dt_of_last_entry\
                                         or p2p.date_confirmed\
                                         or datetime.now()
                    if options["real_run"]:
                        p2p.save()

                    tqdm.write("Updated P2P relation: id: {} ({}) <=> id: {} ({})// DC: {}"
                               .format(from_person.id or "N/A",
                                       from_person.full_name,
                                       to_person.id or "N/A",
                                       to_person.full_name,
                                       p2p.date_confirmed))

                except Person2Person.DoesNotExist:
                    p2p = Person2Person(from_person=from_person,
                                        to_person=to_person,
                                        from_relationship_type="ділові зв'язки",
                                        to_relationship_type="ділові зв'язки",
                                        date_confirmed=candidate.dt_of_last_entry or datetime.now())

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
            "Updated P2C links: {}.\n"
            "Created P2P links: {}."
            .format(updated_companies_total,
                    created_companies_total,
                    failed_companies_total,
                    self.persons_stats["created_total"],
                    self.persons_stats["matched_resolved"],
                    self.persons_stats["matched_not_resolved"],
                    p2c_links_created,
                    p2c_links_updated,
                    p2p_links_total)
        )

    def create_person(self, person_name, is_pep, yob, real_run=False):

        def create_new_person():
            person = Person(
                last_name=title(last_name),
                first_name=title(first_name),
                patronymic=title(patronymic),
                is_pep=is_pep,
                type_of_official=1 if is_pep else 4
            )

            if yob and yob > 1850:
                dob = dt_parse("{}-01-01".format(yob))
                person.dob = dob
                person.dob_details = 2

            if real_run:
                person.save()
                self.new_persons_pk.append(person.pk)

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
            p2c_qs = Person2Company.objects.filter(from_person=person, to_company__edrpou__in=edrpou_list)
            if p2c_qs.count():
                tqdm.write("Matched {}. Found common P2C relation: {}, [{}]"
                           .format(person.full_name, person.url_uk,
                                   " ".join([p2c.to_company.url_uk for p2c in p2c_qs.iterator()])))
                self.persons_dict[person_name] = person
                self.persons_stats["matched_resolved"] += 1

                # Update DoB
                self.update_person_dob(person, yob, real_run)

                return person

        tqdm.write("Found matches for name: {}. Person with same name will be created."
                   .format(person_name))

        self.persons_stats["matched_not_resolved"] += 1
        return create_new_person()

    def update_person_dob(self, person, yob, real_run=False):
        if not person.dob and yob and yob > 1850:
            dob = dt_parse("{}-01-01".format(yob))
            person.dob = dob
            person.dob_details = 2

            tqdm.write("Updated person (id: {}) {} with DOB {}."
                       .format(person.id, person.full_name, person.dob))

        if real_run:
            person.save()

    def company_heads_mapping(self):
        companies_heads_dict = defaultdict(set)

        # select distinct by ("smida_edrpou", "smida_parsed_name") as same person
        # may have more several records of Head position for same company
        company_heads = SMIDACandidate.objects.filter(status="a",
                                              smida_is_real_person=True,
                                              smida_position_class="h") \
            .values_list("smida_edrpou", "smida_parsed_name") \
            .distinct("smida_edrpou", "smida_parsed_name")

        for edrpou, person_name in company_heads:
            companies_heads_dict[edrpou].add(person_name.strip().lower())

        return companies_heads_dict

    def person_2_companies_relations(self):
        person_to_companies = defaultdict(set)

        p2c = SMIDACandidate.objects.filter(status="a",
                                            smida_is_real_person=True) \
            .values_list("smida_edrpou", "smida_parsed_name") \
            .distinct("smida_edrpou", "smida_parsed_name")

        for edrpou, person_name in p2c:
            person_to_companies[person_name.strip().lower()].add(edrpou)

        return person_to_companies

    def all_peps_names(self):
        return [name.strip().lower() for name in SMIDACandidate.objects.filter(status="a",
                                                  smida_is_real_person=True,
                                                  smida_position_class="h")
                    .values_list("smida_parsed_name", flat=True)
                    .distinct("smida_parsed_name")]

    def p2c_get_date_established(self, candidate):
        dat_obr = candidate.matched_json.get("DAT_OBR") or ""

        if dat_obr:
            try:
                dt = dt_parse(dat_obr)
                return dt if dt.date() < date.today() else None
            except (ValueError, OverflowError):
                tqdm.write("Can't parse p2c DAT_OBR for person: {} (ID: {})."
                           .format(candidate.smida_parsed_name, candidate.id))
                return None

    def p2c_get_date_finished(self, candidate):
        termin_obr = candidate.matched_json.get("TERM_OBR") or ""

        if termin_obr:

            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', termin_obr)
            if match and match.group(1):
                try:
                    dt = dt_parse(match.group(1))
                    return dt if dt.date() < date.today() else None
                except (ValueError, OverflowError):
                    tqdm.write("Can't parse p2c TERM_OBR for person: {} (ID: {})."
                               .format(candidate.smida_parsed_name, candidate.id))
                    return None

    def new_persons_having_multiple_company_relations(self):
        qs = Person.objects.filter(pk__in=self.new_persons_pk)\
            .annotate(companies_cnt=Count("related_companies", distinct=True))
        for person in qs.iterator():
            if person.companies_cnt > 1:
                tqdm.write("{} {}".format(person.url_uk, person.companies_cnt))

    def get_companies_last_report(self):
        queryset = SMIDACandidate.objects.filter(status="a", smida_is_real_person=True)\
            .values('smida_edrpou')\
            .annotate(last_report=Max('dt_of_last_entry'))

        result = {}

        for item in queryset:
            key = item['smida_edrpou']

            lr_date = item['last_report']
            if not lr_date:
                continue

            persons = [name.strip().lower() for name in
                       SMIDACandidate.objects.filter(
                           status="a", smida_is_real_person=True,
                           smida_edrpou=key,
                           dt_of_last_entry__date=lr_date.date())
                       .values_list("smida_parsed_name", flat=True)
                       .distinct("smida_parsed_name")]

            result[key] = {
                'date': lr_date,
                'persons': persons
            }

        return result

    def update_p2c_date_established(self, p2c, date_established):
        if not p2c.date_established:
            if not p2c.date_finished:
                p2c.date_established = date_established
                p2c.date_established_details = 0
                return True

            if date_established.date() < p2c.date_finished:
                p2c.date_established = date_established
                p2c.date_established_details = 0
                return True
            return False

        if date_established.date() < p2c.date_established or p2c.date_established_details > 0:
            p2c.date_established = date_established
            p2c.date_established_details = 0
            return True
        return False

    def update_p2c_date_finished(self, p2c, date_finished, df_calculated):
        if not p2c.date_finished:
            p2c.date_finished = date_finished.date()
            p2c.date_finished_details = 0
            return True

        if df_calculated:
            return False

        if p2c.date_finished_details > 0 or date_finished.date() > p2c.date_finished:
            p2c.date_finished = date_finished.date()
            p2c.date_finished_details = 0
            return True
        return False

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
