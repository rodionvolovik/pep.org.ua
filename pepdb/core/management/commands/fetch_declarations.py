# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from dateutil.parser import parse as dt_parse

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Max

from core.models import Person, Declaration
from core.utils import is_initial


class Command(BaseCommand):
    help = ('Loads declarations for PEPs in db')
    TASKS_PER_BATCH = 500

    def add_declaration(self, person, decl, fuzziness, batch, task):
        if task == "link":
            to_link = True
            to_watch = False
        elif task == "monitor":
            to_link = False
            to_watch = True

        if "ft_src" in decl:
            del decl["ft_src"]
        if "index_card" in decl:
            del decl["index_card"]

        params = {
            "last_name": decl["general"]["last_name"],
            "first_name": decl["general"]["name"],
            "patronymic": decl["general"]["patronymic"],
            "position": decl["general"]["post"]["post"],
            "office": decl["general"]["post"]["office"],
            "region": decl["general"]["post"]["region"],
            "year": decl["intro"]["declaration_year"],
            "source": decl,
            "batch_number": batch,
            "url": settings.DECLARATION_DETAILS_ENDPOINT.format(decl["id"]),
            "fuzziness": fuzziness,
            "to_link": to_link,
            "to_watch": to_watch,
        }

        # That's NACP declaration
        if decl["id"].startswith("nacp_"):
            if "nacp_src" in decl:
                del decl["nacp_src"]

            if task == "link":
                allowed_types = ["Щорічна", "Після звільнення"]
                if (person.is_pep and
                        person.declaration_set.filter(nacp_declaration=True, confirmed="a").count() == 0):

                    self.stdout.write(
                        "There are no declarations for poor %s at all, thus extending the scope" % (person,)
                    )

                    allowed_types += ["Перед звільненням", "Після звільнення", "Кандидата на посаду"]
            else:
                allowed_types = ["Перед звільненням", "Після звільнення"]

            if decl["intro"]["doc_type"] not in allowed_types:
                return

            try:
                d = Declaration.objects.get(declaration_id=decl["id"], person_id=person.pk)
                if task == "link":
                    self.stdout.write(
                        "Declaration %s for user %s already exists" % (decl["id"], person)
                    )
                elif task == "monitor":
                    d.to_watch = True
                    d.save()
                return
            except Declaration.MultipleObjectsReturned:
                self.stdout.write(
                    "Declaration %s for user %s already exists too many times" % (decl["id"], person)
                )
                return
            except Declaration.DoesNotExist:
                pass

            params["nacp_declaration"] = True
            if decl["intro"].get("date"):
                params["submitted"] = dt_parse(decl["intro"]["date"]).date()
        else:
            # That's paper declaration
            if task == "monitor":
                # There are nothing to monitor, paper based declarations was submitted only
                # annually or before applying for the position, not on resign
                return
            elif task == "link":
                try:
                    d = Declaration.objects.get(declaration_id=decl["id"], person_id=person.pk)

                    self.stdout.write(
                        "Declaration %s for user %s already exists" % (decl["id"], person)
                    )
                    return
                except Declaration.DoesNotExist:
                    pass

        d = Declaration.objects.create(
            declaration_id=decl["id"],
            person=person,
            **params
        )

        if not d.family:
            d.relatives_populated = True
            d.save()

        return True

    def handle(self, *args, **options):
        max_batch = Declaration.objects.aggregate(mx=Max("batch_number"))

        current_batch = max_batch.get("mx", 0) + 1
        task_number = 0

        if options["type"] == "link":
            persons = Person.objects.all().nocache()
        elif options["type"] == "monitor":
            persons = Person.objects.filter(is_pep=True).nocache()

        for person in persons:
            full_name = ("%s %s %s" % (person.first_name, person.patronymic,
                                       person.last_name)).replace("  ", " ")
            full_name = full_name.strip()

            if is_initial(person.first_name) or is_initial(person.patronymic):
                self.stdout.write(
                    "Not pulling %s because of initials" % full_name
                )

                continue

            names_to_retrieve = [full_name]

            if person.also_known_as_uk:
                names_to_retrieve += list(
                    filter(
                        None,
                        map(
                            unicode.strip,
                            person.also_known_as_uk.replace(",", "\n").split("\n")
                        )
                    )
                )

            for full_name_to_ret in names_to_retrieve:
                subr = requests.get(
                    settings.DECLARATIONS_SEARCH_ENDPOINT, params={
                        "q": full_name_to_ret,
                        "format": "json"
                    }, verify=False, timeout=60).json()

                self.stdout.write(full_name_to_ret)

                for decl in subr["results"]["object_list"]:
                    if options["type"] == "link":
                        batch = current_batch + task_number // self.TASKS_PER_BATCH
                    elif options["type"] == "monitor":
                        batch = -100

                    res = self.add_declaration(
                        person,
                        decl,
                        subr["fuzziness"],
                        batch,
                        options["type"]
                    )

                    if res:
                        task_number += 1

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=["link", "monitor"],
            required=True,
            help='Pull declarations for linking or monitoring of resign',
        )
