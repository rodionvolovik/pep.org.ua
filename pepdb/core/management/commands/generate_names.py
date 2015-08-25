# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Person, Ua2RuDictionary
from core.utils import is_cyr, is_ukr
from translitua import translit, ALL_RUSSIAN, ALL_UKRAINIAN


class Command(BaseCommand):

    def handle(self, *args, **options):
        ru_translations = {}

        for t in Ua2RuDictionary.objects.all():
            ru_translations[t.term.lower()] = filter(None, [
                t.translation, t.alt_translation
            ])

        for person in Person.objects.all():
            first_names = []
            last_names = []
            patronymics = []

            original = ["{} {} {}".format(
                person.last_name, person.first_name, person.patronymic
            ).strip().replace("  ", " ")]

            result = set()

            if (person.first_name.lower() in ru_translations and
                    is_cyr(person.first_name)):
                first_names = ru_translations[person.first_name.lower()]
            else:
                first_names = [person.first_name]

            if (person.last_name.lower() in ru_translations and
                    is_cyr(person.last_name)):
                last_names = ru_translations[person.last_name.lower()]
            else:
                last_names = [person.last_name]

            if (person.patronymic.lower() in ru_translations and
                    is_cyr(person.patronymic)):
                patronymics = ru_translations[person.patronymic.lower()]
            else:
                patronymics = [person.patronymic]

            translated = [
                "{} {} {}".format(l, f, p).strip().replace("  ", " ")
                for f in first_names
                for p in patronymics
                for l in last_names
            ]

            for n in original:
                if is_cyr(n):
                    # TODO: also replace double ж, х, ц, ч, ш with single chars
                    for ua_table in ALL_UKRAINIAN:
                        result.add(translit(n, ua_table))

            for n in translated:
                if not is_ukr(n):
                    for ru_table in ALL_RUSSIAN:
                        result.add(translit(n, ru_table))

            person.names = "\n".join(result | set(translated))
            person.save()
