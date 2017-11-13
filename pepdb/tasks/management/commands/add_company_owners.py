# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings
from django.db.utils import DataError

from elasticsearch_dsl import Q

from core.models import Person, Company, Person2Company
from core.utils import parse_fullname

from tasks.elastic_models import EDRPOU


class Command(BaseCommand):
    help = """

    """
    status_order = (
        "зареєстровано",
        "зареєстровано, свідоцтво про державну реєстрацію недійсне",
        "порушено справу про банкрутство",
        "порушено справу про банкрутство (санація)",
        "в стані припинення",
        "припинено",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Connect persons to banks for real',
        )

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)

        successful = 0
        failed = 0

        exact_matches = 0
        fuzzy_matches = 0
        connections_created = 0
        persons_created = 0

        for company in Company.objects.filter(state_company=True).exclude(edrpou=""):
            k = company.edrpou.lstrip("0")

            # Because open copy of registry has no dates and some of companies
            # has more than one record we are using heuristic here to determine
            # latest record using registration status (they have "priorities")
            for order in self.status_order:
                res = EDRPOU.search().query(
                    "bool",
                    must=[
                        Q("term", edrpou=k),
                        Q("term", status=order)
                    ]
                )
                ans = res.execute()
                if ans:
                    break

            # Last attempt
            if not ans:
                res = EDRPOU.search().query(
                    "term",
                    edrpou=k,
                )
                ans = res.execute()

            if len(ans) > 1:
                self.stderr.write(
                    "Too many companies found by code %s, for the name %s, skipping" %
                    (k, company)
                )

                failed += 1
                continue

            if len(ans) == 0:
                self.stderr.write("Cannot find the company by code %s" % (k, ))

                failed += 1
                continue

            edr_company = ans[0]
            if not edr_company.head:
                self.stderr.write(
                    "Cannot find head for the company %s, (%s)" %
                    (ans[0].name, k)
                )

                failed += 1
                continue

            successful += 1
            lastname, firstname, patronymic, _ = parse_fullname(edr_company.head)

            exact_links = Person2Company.objects.select_related("from_person").filter(
                to_company_id=company.pk,
                from_person__first_name__iexact=firstname,
                from_person__last_name__iexact=lastname
            )

            if patronymic:
                exact_links = exact_links.filter(from_person__patronymic__iexact=patronymic)

            if exact_links.count():
                exact_matches += 1
                for l in exact_links:
                    l.created_from_edr = True
                    l.date_confirmed = edr_company.last_update
                    l.date_confirmed_details = 0
                    l.save()

                    if l.relationship_type != "Керівник":
                        self.stdout.write("Relation %s exists but has different type: %s" % (
                            l, l.relationship_type))

                continue
            else:
                fuzzy_links = Person2Company.objects.select_related("from_person").filter(
                    to_company_id=company.pk,
                    from_person__last_name__iexact=lastname,
                    from_person__first_name__istartswith=firstname[0],
                )

                if patronymic:
                    fuzzy_links = fuzzy_links.filter(
                        from_person__patronymic__istartswith=patronymic[0])

                if fuzzy_links:
                    fuzzy_matches += 1
                    for l in fuzzy_links:
                        l.created_from_edr = True
                        l.date_confirmed = edr_company.last_update
                        l.date_confirmed_details = 0
                        l.save()

                        self.stdout.write("Fuzzy match: %s vs %s" % (edr_company.head, l.from_person.full_name))

                        if l.relationship_type != "Керівник":
                            self.stdout.write("Relation %s exists but has different type: %s" % (
                                l, l.relationship_type))

                    continue

            try:
                if options["real_run"]:
                    person = Person.objects.create(
                        first_name=firstname,
                        last_name=lastname,
                        patronymic=patronymic,
                        is_pep=True,
                        type_of_official=1
                    )
                persons_created += 1

                if options["real_run"]:
                    Person2Company.objects.create(
                        from_person=person,
                        to_company=company,
                        relationship_type="Керівник",
                        is_employee=True,
                        created_from_edr=True,
                        date_confirmed=edr_company.last_update,
                        # TODO: decide what to do with connection proofs
                        proof_title="Інформація, отримана з ЄДР",
                    )

                connections_created += 1
            except DataError:
                self.stdout.write("Cannot create %s person or connection" % edr_company.head)

        self.stdout.write(
            "Creation failed: %s, creation successful: %s" % (failed, successful)
        )
        self.stdout.write(
            "Exact matches: %s, fuzzy matches: %s" %
            (exact_matches, fuzzy_matches)
        )
        self.stdout.write(
            "Persons created: %s, connections created: %s" %
            (persons_created, connections_created)
        )
