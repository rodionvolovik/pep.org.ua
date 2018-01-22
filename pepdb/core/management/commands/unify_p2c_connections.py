# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unicodecsv import reader

from django.core.management.base import BaseCommand
from django.db.models.functions import Lower
from django.db.utils import IntegrityError

from core.model.translations import Ua2EnDictionary
from core.models import Person2Company
from core.utils import lookup_term


class Command(BaseCommand):
    def handle(self, *args, **options):
        positions = {}
        with open("core/dicts/unified_positions.csv", "r") as fp:
            r = reader(fp)

            for l in r:
                positions[l[0].lower().strip()] = l[1].strip()

        for p2c in Person2Company.objects.annotate(
                rt_lower=Lower("relationship_type_uk")).filter(
                rt_lower__in=positions.keys()).nocache():

            p2c.relationship_type_uk = positions[p2c.relationship_type_uk.lower()]

            term = lookup_term(p2c.relationship_type_uk)
            t = Ua2EnDictionary.objects.filter(
                term__iexact=term).first()

            if t and t.translation:
                self.relationship_type_en = t.translation
            else:
                self.stderr.write("Cannot translate {} into english, leaving translation {}".format(
                    p2c.relationship_type_uk,
                    p2c.relationship_type_en
                ))

                try:
                    Ua2EnDictionary.objects.create(
                        term=term
                    )
                except IntegrityError:
                    # No need to turn alarm on, if the value is already in db
                    pass

            p2c.save()
