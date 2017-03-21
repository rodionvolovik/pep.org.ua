# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Max

from core.models import Person, Declaration
from core.utils import is_initial



class Command(BaseCommand):
    help = ('Loads declarations for PEPs in db')
    TASKS_PER_BATCH = 25

    def add_declaration(self, person, decl, fuzziness, batch):
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
                    "batch_number": batch,                    
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
                    "batch_number": batch,
                    "url": "https://declarations.com.ua/declaration/%s" % (
                        decl["id"]),
                    "fuzziness": fuzziness
                }
            )

        return True

    def handle(self, *args, **options):
        max_batch = Declaration.objects.aggregate(mx=Max("batch_number"))

        current_batch = max_batch.get("mx", 0) + 1
        task_number = 0

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
                res = self.add_declaration(
                    person,
                    decl,
                    subr["fuzziness"],
                    current_batch + task_number // self.TASKS_PER_BATCH
                )

                if res:
                    task_number += 1
