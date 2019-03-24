# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db.models import Q, F
from core.models import Declaration, Ua2EnDictionary, Company, Person2Company, Person
from core.utils import lookup_term, get_localized_field, localized_field


class Command(BaseCommand):
    def handle(self, *args, **options):
        en_translations = {}

        for t in Ua2EnDictionary.objects.exclude(translation="").nocache():
            en_translations[lookup_term(t.term)] = t.translation

        for p in (
            Declaration.objects.filter(confirmed="a").defer("source").all().nocache()
        ):
            if lookup_term(get_localized_field(p, "region")) in en_translations:
                p.region_en = en_translations[lookup_term(get_localized_field(p, "region"))]

            if lookup_term(get_localized_field(p, "position")) in en_translations:
                p.position_en = en_translations[lookup_term(get_localized_field(p, "position"))]

            if lookup_term(get_localized_field(p, "office")) in en_translations:
                p.office_en = en_translations[lookup_term(get_localized_field(p, "office"))]

            p.save()

        for c in Company.objects.filter(
            Q(name_en="")
            | Q(short_name_en="")
            | Q(name_en__isnull=True)
            | Q(short_name_en__isnull=True)
        ).nocache():
            c.save()  # This will invoke translation on the save method

        for p2c in Person2Company.objects.filter(
            Q(relationship_type_en="") | Q(relationship_type_en__isnull=True) |
            Q(relationship_type_en=F(localized_field("relationship_type")))
        ).nocache():
            p2c.save()  # This will invoke translation on the save method

        for p in (
            Person.objects.exclude(
                Q(**{localized_field("city_of_birth"): ""}) | Q(**{localized_field("city_of_birth") + "__isnull": True})
            )
            .filter(Q(city_of_birth_en="") | Q(city_of_birth_en__isnull=True) | Q(city_of_birth_en=F(localized_field("city_of_birth"))))
            .nocache()
        ):
            p.save()  # This will invoke translation on the save method
