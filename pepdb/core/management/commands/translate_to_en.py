# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import Declaration, Ua2EnDictionary, Company, Person2Company
from core.utils import lookup_term


class Command(BaseCommand):
    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.exclude(translation=""):
            en_translations[lookup_term(t.term)] = t.translation

        for p in Declaration.objects.filter(confirmed="a").all():
            if lookup_term(p.region_uk) in en_translations:
                p.region_en = en_translations[lookup_term(p.region_uk)]

            if lookup_term(p.position_uk) in en_translations:
                p.position_en = en_translations[lookup_term(p.position_uk)]

            if lookup_term(p.office_uk) in en_translations:
                p.office_en = en_translations[lookup_term(p.office_uk)]

            p.save()

        for c in Company.objects.filter(
                Q(name_en="") | Q(short_name_en="") | Q(name_en__isnull=True) |
                Q(short_name__isnull=True)):
            c.save()  # This will invoke translation on the save method

        for p2c in Person2Company.objects.filter(
                Q(relationship_type_en="") |
                Q(relationship_type_en__isnull=True)):
            p2c.save()  # This will invoke translation on the save method
