# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Declaration, Ua2EnDictionary


class Command(BaseCommand):
    args = '<file_path>'

    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.all():
            en_translations[t.term.lower()] = filter(None, [
                t.translation, t.alt_translation
            ])

        not_translated_regions = set()
        not_translated_positions = set()
        not_translated_offices = set()
        for p in Declaration.objects.filter(confirmed="a").all():
            if (p.region_uk.lower() not in en_translations):
                not_translated_regions.add(p.region_uk.lower())

            if (p.position_uk.lower() not in en_translations):
                not_translated_positions.add(p.position_uk.lower())

            if (p.office_uk.lower() not in en_translations):
                not_translated_offices.add(p.office_uk.lower())

        for x in [not_translated_regions, not_translated_positions,
                  not_translated_offices]:
            for term in x:
                Ua2EnDictionary.objects.create(
                    term=term
                )
