# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import Declaration, Ua2EnDictionary, Company, Person2Company, Person
from core.utils import lookup_term


class Command(BaseCommand):
    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.exclude(translation="").nocache():
            en_translations[lookup_term(t.term)] = t.translation

        for p in Declaration.objects.filter(confirmed="a").defer("source").all().nocache():
            if lookup_term(p.region_uk) in en_translations:
                p.region_en = en_translations[lookup_term(p.region_uk)]

            if lookup_term(p.position_uk) in en_translations:
                p.position_en = en_translations[lookup_term(p.position_uk)]

            if lookup_term(p.office_uk) in en_translations:
                p.office_en = en_translations[lookup_term(p.office_uk)]

            p.save()

        for c in Company.objects.filter(
                Q(name_en="") | Q(short_name_en="") | Q(name_en__isnull=True) |
                Q(short_name_en__isnull=True)).nocache():
            c.save()  # This will invoke translation on the save method

        for p2c in Person2Company.objects.filter(
                Q(relationship_type_en="") |
                Q(relationship_type_en__isnull=True)).nocache():
            p2c.save()  # This will invoke translation on the save method

        for p in Person.objects \
                .exclude(Q(city_of_birth_uk="") | Q(city_of_birth_uk__isnull=True)) \
                .filter(Q(city_of_birth_en="") | Q(city_of_birth_en__isnull=True)).nocache():
            p.save()  # This will invoke translation on the save method
