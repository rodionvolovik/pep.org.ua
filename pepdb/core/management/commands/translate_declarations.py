# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Declaration, Ua2EnDictionary


class Command(BaseCommand):
    args = '<file_path>'

    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.exclude(translation=""):
            en_translations[t.term.lower()] = t.translation

        for p in Declaration.objects.filter(confirmed="a").all():
            if p.region_uk.lower() in en_translations:
                p.region_en = en_translations[p.region_uk.lower()]

            if p.position_uk.lower() in en_translations:
                p.position_en = en_translations[p.position_uk.lower()]

            if p.office.lower() in en_translations:
                p.office_en = en_translations[p.office_uk.lower()]

            p.save()
