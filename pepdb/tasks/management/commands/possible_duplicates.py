# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.core.management.base import BaseCommand
from django.conf import settings

from collections import defaultdict
from core.models import Person
from core.utils import is_initial
from tasks.models import PersonDeduplication


class Command(BaseCommand):
    help = ('Finds potential duplicates in DB and stores them as tasks for '
            'manual resolution')

    def handle(self, *args, **options):
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

        grouped_by_fullname = defaultdict(list)
        grouped_by_shortenedname = defaultdict(list)

        for l in all_persons:
            if l["has_initials"] == "True":
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

        # Second pass
        for l in all_persons:
            if l["pk"] not in spoiled_ids:
                mixed_grouping[l["key"]].append(l["pk"])

        for k, v in mixed_grouping.items():
            if len(v) > 1:
                spoiled_ids |= set(v)
                chunks_to_review.append(v)

        for chunk in chunks_to_review:
            PersonDeduplication(
                person1_id=chunk[0],
                person2_id=chunk[1],
            ).save()
