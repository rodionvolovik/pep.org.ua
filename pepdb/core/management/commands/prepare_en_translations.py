# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from core.models import (
    Declaration,
    Ua2EnDictionary,
    Company,
    Person2Company,
    Person,
    RelationshipProof,
)
from core.utils import lookup_term, get_localized_field


class Command(BaseCommand):
    args = "<file_path>"

    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.all().nocache():
            en_translations[lookup_term(t.term)] = filter(
                None, [t.translation, t.alt_translation]
            )

        not_translated_regions = set()
        not_translated_positions = set()
        not_translated_offices = set()
        not_translated_cities = set()
        not_translated_proofs = set()

        for p in (
            Declaration.objects.filter(confirmed="a").defer("source").all().nocache().iterator()
        ):
            if lookup_term(get_localized_field(p, "region")) not in en_translations:
                not_translated_regions.add(lookup_term(get_localized_field(p, "region")))

            if lookup_term(get_localized_field(p, "position")) not in en_translations:
                not_translated_positions.add(lookup_term(get_localized_field(p, "position")))

            if lookup_term(get_localized_field(p, "office")) not in en_translations:
                not_translated_offices.add(lookup_term(get_localized_field(p, "office")))

        for p in Person.objects.all().nocache().iterator():
            if (
                not get_localized_field(p, "city_of_birth")
                and lookup_term(get_localized_field(p, "city_of_birth")) not in en_translations
            ):
                not_translated_cities.add(get_localized_field(p, "city_of_birth"))

        for c in Company.objects.all().nocache().iterator():
            if not c.name_en and lookup_term(get_localized_field(c, "name")) not in en_translations:
                not_translated_offices.add(lookup_term(get_localized_field(c, "name")))

            if (
                not c.short_name_en
                and lookup_term(get_localized_field(c, "short_name")) not in en_translations
            ):
                not_translated_offices.add(lookup_term(get_localized_field(c, "short_name")))

        for p2c in Person2Company.objects.all().nocache():
            if (
                not p2c.relationship_type_en
                and lookup_term(get_localized_field(p2c, "relationship_type")) not in en_translations
            ):
                not_translated_positions.add(lookup_term(get_localized_field(p2c, "relationship_type")))

        for r in RelationshipProof.objects.all().nocache():
            if (
                not r.proof_title_en
                and
                # "pdf" not in r.proof_title_uk.lower() and
                # "jpg" not in r.proof_title_uk.lower() and
                lookup_term(get_localized_field(r, "proof_title")) not in en_translations
            ):
                not_translated_proofs.add(lookup_term(get_localized_field(r, "proof_title")))

        x = (
            not_translated_regions
            | not_translated_positions
            | not_translated_offices
            | not_translated_cities
            | not_translated_proofs
        )

        for term in x:
            if not term:
                continue

            try:
                Ua2EnDictionary.objects.create(term=term)
            except IntegrityError:
                # No need to turn alarm on, if the value is already in db
                pass
