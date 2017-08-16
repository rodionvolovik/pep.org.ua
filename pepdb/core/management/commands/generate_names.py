# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from core.models import Person, Ua2RuDictionary
from core.utils import is_cyr, is_ukr, parse_fullname
from translitua import translit, ALL_RUSSIAN, ALL_UKRAINIAN


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        self.ru_translations = {}

        for t in Ua2RuDictionary.objects.all():
            self.ru_translations[t.term.lower()] = filter(None, [
                t.translation, t.alt_translation
            ])

        return super(Command, self).__init__(*args, **kwargs)

    def add_for_translation(self, name):
        if name:
            try:
                Ua2RuDictionary.objects.create(term=name)
            except IntegrityError:
                pass

    def transliterate(self, person_last_name, person_first_name,
                      person_patronymic):
        first_names = []
        last_names = []
        patronymics = []

        original = ["{} {} {}".format(
            person_last_name, person_first_name, person_patronymic
        ).strip().replace("  ", " ")]

        result = set()

        if (person_first_name.lower() in self.ru_translations and
                is_cyr(person_first_name)):
            first_names = self.ru_translations[person_first_name.lower()]
        else:
            first_names = [person_first_name]
            self.add_for_translation(person_first_name)

        if (person_last_name.lower() in self.ru_translations and
                is_cyr(person_last_name)):
            last_names = self.ru_translations[person_last_name.lower()]
        else:
            last_names = [person_last_name]
            self.add_for_translation(person_last_name)

        if (person_patronymic.lower() in self.ru_translations and
                is_cyr(person_patronymic)):
            patronymics = self.ru_translations[person_patronymic.lower()]
        else:
            patronymics = [person_patronymic]
            self.add_for_translation(person_patronymic)

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

        return result | set(translated)

    def handle(self, *args, **options):
        for person in Person.objects.all():
            person.last_name_uk = person.last_name_uk or ""
            person.first_name_uk = person.first_name_uk or ""
            person.patronymic_uk = person.patronymic_uk or ""

            names = self.transliterate(
                person.last_name_uk, person.first_name_uk,
                person.patronymic_uk
            )

            if person.also_known_as_uk:
                for aka_name in filter(None, person.also_known_as_uk.split("\n")):
                    last_name, first_name, patronymic, _ = parse_fullname(aka_name)
                    names |= self.transliterate(
                        last_name, first_name, patronymic
                    )

            person.names = "\n".join(names)

            person.first_name_uk = person.first_name_uk.strip()
            person.last_name_uk = person.last_name_uk.strip()
            person.patronymic_uk = person.patronymic_uk.strip()

            if len(person.first_name) == 1:
                person.first_name += "."

            if len(person.patronymic) == 1:
                person.patronymic += "."

            person.save()
