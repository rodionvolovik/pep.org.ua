# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from core.models import Person, Declaration


class Command(BaseCommand):
    help = ('Loads declarations for PEPs in db')

    def add_declaration(self, person, decl, fuzziness):
        Declaration.objects.update_or_create(
            declaration_id=decl["id"],
            person=person,
            defaults={
                "last_name": decl["general"]["last_name"],
                "first_name": decl["general"]["name"],
                "patronymic": decl["general"]["patronymic"],
                "position": decl["general"]["post"]["post"],
                "office": decl["general"]["post"]["office"],
                "region": decl["general"]["post"]["region"],
                "year": decl["intro"]["declaration_year"],
                "source": decl,
                "url": "http://declarations.com.ua/declaration/%s" % (
                    decl["id"]),
                "fuzziness": fuzziness
            }
        )

    def handle(self, *args, **options):
        for person in Person.objects.all():
            full_name = ("%s %s %s" % (person.first_name, person.patronymic,
                                       person.last_name)).replace("  ", " ")
            full_name = full_name.strip()

            subr = requests.get(
                settings.DECLARATIONS_ENDPOINT, params={
                    "q": full_name,
                    "format": "json"
                }).json()

            for decl in subr["results"]["object_list"]:
                self.add_declaration(person, decl, subr["fuzziness"])
