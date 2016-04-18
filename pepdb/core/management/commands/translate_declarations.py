# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Declaration, Ua2EnDictionary
from core.utils import lookup_term


class Command(BaseCommand):
    args = '<file_path>'

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
