# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from core.models import Person, Ua2RuDictionary
from unicodecsv import writer


class Command(BaseCommand):
    args = "<file_path>"

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError("First argument must be a result file")

        first_names = set()
        last_names = set()
        patronymics = set()

        for p in Person.objects.all():
            first_names.add(p.first_name.lower())
            last_names.add(p.last_name.lower())
            patronymics.add(p.patronymic.lower())

        with open(file_path, "w") as fp:
            w = writer(fp)

            w.writerow(["term", "translation", "alt_translation", "comments"])

            for t in Ua2RuDictionary.objects.all():
                comment = ""
                if t.comments in ["Ім'я", "По-батькові", "Прізвище"]:
                    w.writerow([t.term, t.translation, t.alt_translation, t.comments])
                else:
                    if t.term.lower() in first_names:
                        comment = "Ім'я"
                    elif t.term.lower() in patronymics:
                        comment = "По-батькові"
                    elif t.term.lower() in last_names:
                        comment = "Прізвище"

                    w.writerow([t.term, t.translation, t.alt_translation, comment])
