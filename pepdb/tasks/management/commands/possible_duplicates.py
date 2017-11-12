# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.db.utils import IntegrityError
from django.conf import settings

from collections import defaultdict
from core.models import Person
from core.utils import is_initial, parse_fullname
from tasks.models import PersonDeduplication
from Levenshtein import jaro
from itertools import combinations


class Command(BaseCommand):
    help = ('Finds potential duplicates in DB and stores them as tasks for '
            'manual resolution')

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        all_persons = []

        keys = ["pk", "key", "fullname", "has_initials", "last_name",
                "first_name", "patronymic"]

        for p in Person.objects.all():
            all_persons.append(dict(zip(keys, [
                p.pk,
                ("%s %s %s" % (
                    p.last_name, p.first_name[:1], p.patronymic[:1])).lower(),
                ("%s %s %s" % (
                    p.last_name, p.first_name, p.patronymic)).lower(),
                is_initial(p.first_name) or is_initial(p.patronymic),
                p.last_name,
                p.first_name,
                p.patronymic])))

            for aka in map(unicode.strip, (p.also_known_as_uk or "").replace(",", "\n").split("\n")):
                if not aka:
                    continue

                last_name, first_name, patronymic, _ = parse_fullname(aka)
                if not(all([last_name, first_name, patronymic])):
                    continue

                all_persons.append(dict(zip(keys, [
                    p.pk,
                    ("%s %s %s" % (
                        last_name, first_name[:1], patronymic[:1])).lower(),
                    ("%s %s %s" % (
                        last_name, first_name, patronymic)).lower(),
                    is_initial(first_name) or is_initial(patronymic),
                    last_name,
                    first_name,
                    patronymic])))

        grouped_by_fullname = defaultdict(list)
        grouped_by_shortenedname = defaultdict(list)

        # First pass: exact matches by full name (even if those are given with initials)
        for l in all_persons:
            if l["has_initials"]:
                grouped_by_shortenedname[l["key"]].append(l["pk"])
            else:
                grouped_by_fullname[l["fullname"]].append(l["pk"])

        spoiled_ids = set()
        chunks_to_review = list()

        for k, v in grouped_by_fullname.items():
            if len(v) > 1:
                spoiled_ids |= set(v)
                chunks_to_review.append(v)

        for k, v in grouped_by_shortenedname.items():
            if len(v) > 1:
                spoiled_ids |= set(v)
                chunks_to_review.append(v)

        mixed_grouping = defaultdict(list)

        # Second pass: initials vs full names
        for l in all_persons:
            if l["pk"] not in spoiled_ids and l["has_initials"]:
                mixed_grouping[l["key"]].append(l["pk"])

        for l in all_persons:
            if l["pk"] not in spoiled_ids and not l["has_initials"] and l["key"] in mixed_grouping:
                mixed_grouping[l["key"]].append(l["pk"])

        for k, v in mixed_grouping.items():
            if len(v) > 1:
                spoiled_ids |= set(v)
                chunks_to_review.append(v)

        for chunk in chunks_to_review:
            try:
                PersonDeduplication(
                    person1_id=chunk[0],
                    person2_id=chunk[1],
                    person1_json=Person.objects.get(pk=chunk[0]).to_dict(),
                    person2_json=Person.objects.get(pk=chunk[1]).to_dict(),
                ).save()
            except IntegrityError:
                pass

        candidates_for_fuzzy = [
            l for l in all_persons
            if l["pk"] not in spoiled_ids and not l["has_initials"]
        ]

        for a, b in combinations(candidates_for_fuzzy, 2):
            score = jaro(a["fullname"], b["fullname"])
            if score > 0.93:
                try:
                    PersonDeduplication(
                        person1_id=a["pk"],
                        person2_id=b["pk"],
                        fuzzy=True,
                        person1_json=Person.objects.get(pk=a["pk"]).to_dict(),
                        person2_json=Person.objects.get(pk=b["pk"]).to_dict(),
                    ).save()
                except IntegrityError:
                    pass
