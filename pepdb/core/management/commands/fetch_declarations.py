# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from core.models import Person, Declaration


def is_initial(s):
    return len(s) == 1 or s.endswith(".")


class Command(BaseCommand):
    help = ('Loads declarations for PEPs in db')

    def add_declaration(self, person, decl, fuzziness):
        try:
            _ = Declaration.objects.get(declaration_id=decl["id"])
            self.stdout.write(
                "Declaration %s already exists" % decl["id"]
            )
            return
        except Declaration.MultipleObjectsReturned:
            self.stdout.write(
                "Declaration %s already exists too many times" % decl["id"]
            )
            return
        except Declaration.DoesNotExist:
            pass

        if decl["id"].startswith("nacp_"):
            if "nacp_src" in decl:
                del decl["nacp_src"]

            if decl["intro"]["doc_type"] != "Щорічна":
                return

            subr = requests.get(
                "https://public-api.nazk.gov.ua/v1/declaration/%s" % (
                    decl["id"].replace("nacp_", "")
                ), verify=False).json()

            decl["nacp_response"] = subr
            Declaration.objects.create(
                declaration_id=decl["id"],
                person=person,
                **{
                    "last_name": decl["general"]["last_name"],
                    "first_name": decl["general"]["name"],
                    "patronymic": decl["general"]["patronymic"],
                    "position": decl["general"]["post"]["post"],
                    "office": decl["general"]["post"]["office"],
                    "region": decl["general"]["post"]["region"],
                    "year": decl["intro"]["declaration_year"],
                    "source": decl,
                    "nacp_declaration": True,
                    "url": "https://declarations.com.ua/declaration/%s" % (
                        decl["id"]),
                    "fuzziness": fuzziness
                }
            )
        else:
            if "ft_src" in decl:
                del decl["ft_src"]

            Declaration.objects.create(
                declaration_id=decl["id"],
                person=person,
                **{
                    "last_name": decl["general"]["last_name"],
                    "first_name": decl["general"]["name"],
                    "patronymic": decl["general"]["patronymic"],
                    "position": decl["general"]["post"]["post"],
                    "office": decl["general"]["post"]["office"],
                    "region": decl["general"]["post"]["region"],
                    "year": decl["intro"]["declaration_year"],
                    "source": decl,
                    "url": "https://declarations.com.ua/declaration/%s" % (
                        decl["id"]),
                    "fuzziness": fuzziness
                }
            )

    def handle(self, *args, **options):
        for person in Person.objects.all():
            full_name = ("%s %s %s" % (person.first_name, person.patronymic,
                                       person.last_name)).replace("  ", " ")
            full_name = full_name.strip()

            if is_initial(person.first_name) or is_initial(person.patronymic):
                self.stdout.write(
                    "Not pulling %s because of initials" % full_name
                )

                continue

            subr = requests.get(
                settings.DECLARATIONS_ENDPOINT, params={
                    "q": full_name,
                    "format": "json"
                }, verify=False).json()

            self.stdout.write(full_name)

            for decl in subr["results"]["object_list"]:
                self.add_declaration(person, decl, subr["fuzziness"])
