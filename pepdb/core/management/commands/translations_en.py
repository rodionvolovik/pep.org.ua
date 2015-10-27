# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from core.models import Company, Person2Company
from core.utils import title, is_cyr
from unicodecsv import writer


class Command(BaseCommand):
    args = '<file_path>'

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a result file')

        positions = set()
        companies = set()

        for c in Company.objects.filter(name_en=""):
            if c.name_ua:
                companies.add(c.name_ua)

        for p2c in Person2Company.objects.filter(relationship_type_en=""):
            if p2c.relationship_type_ua:
                positions.add(p2c.relationship_type_ua)

        with open(file_path, "w") as fp:
            w = writer(fp)

            for x in companies:
                w.writerow([x, ""])

            for x in positions:
                w.writerow([x, ""])
