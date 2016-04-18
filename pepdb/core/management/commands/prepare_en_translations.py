# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Declaration, Ua2EnDictionary
from core.utils import lookup_term


class Command(BaseCommand):
    args = '<file_path>'

    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.all():
            en_translations[lookup_term(t.term)] = filter(None, [
                t.translation, t.alt_translation
            ])

        not_translated_regions = set()
        not_translated_positions = set()
        not_translated_offices = set()
        for p in Declaration.objects.filter(confirmed="a").all():
            if (lookup_term(p.region_uk) not in en_translations):
                not_translated_regions.add(lookup_term(p.region_uk))

            if (lookup_term(p.position_uk) not in en_translations):
                not_translated_positions.add(lookup_term(p.position_uk))

            if (lookup_term(p.office_uk) not in en_translations):
                not_translated_offices.add(lookup_term(p.office_uk))

        for x in [not_translated_regions, not_translated_positions,
                  not_translated_offices]:
            for term in x:
                Ua2EnDictionary.objects.create(
                    term=term
                )
