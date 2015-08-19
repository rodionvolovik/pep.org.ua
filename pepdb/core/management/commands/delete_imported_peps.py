# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from core.models import Person
from django.core.urlresolvers import reverse


class Command(BaseCommand):
    help = ('Deletes vanilla records from google table')

    def print_person(self, msg, person):
        self.stdout.write(
            "{}: {}, {}".format(
                msg,
                person,
                reverse('admin:core_person_change', args=[person.id]))
        )

    def handle(self, *args, **options):
        qs = Person.objects.filter(
            is_pep=True,
            type_of_official=1,
            city_of_birth="",
            registration="",
            passport_id="",
            passport_reg="",
            tax_payer_id="",
            id_number="",
            reputation_assets="",
            reputation_sanctions="",
            reputation_crimes="",
            reputation_manhunt="",
            reputation_convictions="",
            wiki="",
            risk_category="low"
        )

        for person in qs:
            if person.person2company_set.count() != 1:
                self.print_person(
                    "Too many companies: {}".format(
                        person.person2company_set.count()),
                    person)
                continue

            if person.to_persons.count() != 0:
                self.print_person(
                    "Too many to_persons: {}".format(
                        person.to_persons.count()),
                    person)
                continue

            if person.from_persons.count() != 0:
                self.print_person(
                    "Too many from_persons: {}".format(
                        person.from_persons.count()),
                    person)
                continue

            if person.person2country_set.count() != 0:
                self.print_person(
                    "Too many countries: {}".format(
                        person.person2country_set.count()),
                    person)
                continue

            person.delete()
