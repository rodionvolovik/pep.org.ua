# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Ua2EnDictionary
from unicodecsv import writer
from django.db.models import Q


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_path", help="CSV file to export translations")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        with open(file_path, "w") as fp:
            w = writer(fp)
            for t in Ua2EnDictionary.objects.filter(
                Q(translation__isnull=True) | Q(translation="")
            ):
                w.writerow([t.term, t.translation])
