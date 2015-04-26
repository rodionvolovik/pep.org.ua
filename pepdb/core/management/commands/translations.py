# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.core.management.base import BaseCommand, CommandError
from core.models import Person, Ua2RuDictionary
from core.utils import title
from unicodecsv import writer


def is_cyr(name):
    return re.search("[а-яіїєґ]+", name.lower(), re.UNICODE) is not None


class Command(BaseCommand):
    args = '<file_path>'

    def handle(self, *args, **options):
        try:
            file_path = args[0]
        except IndexError:
            raise CommandError('First argument must be a result file')

        ru_translations = {}

        for t in Ua2RuDictionary.objects.all():
            ru_translations[t.term.lower()] = filter(None, [
                t.translation, t.alt_translation
            ])

        not_translated_first_names = []
        not_translated_last_names = []
        not_translated_patronymics = []
        for p in Person.objects.all():
            if p.first_name.lower() not in ru_translations and is_cyr(p.first_name):
                not_translated_first_names.append(title(p.first_name))

            if p.last_name.lower() not in ru_translations and is_cyr(p.last_name):
                not_translated_last_names.append(title(p.last_name))

            if p.patronymic.lower() not in ru_translations and is_cyr(p.patronymic):
                not_translated_patronymics.append(title(p.patronymic))

        with open(file_path, "w") as fp:
            w = writer(fp)

            for x in set(not_translated_first_names):
                w.writerow([x, ""])

            for x in set(not_translated_patronymics):
                w.writerow([x, ""])

            for x in set(not_translated_last_names):
                w.writerow([x, ""])
