# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.db.utils import IntegrityError
from django.db.models import Q
from django.conf import settings

from collections import defaultdict
from core.models import Company
from tasks.models import CompanyDeduplication
from Levenshtein import jaro
from itertools import combinations, product


class Command(BaseCommand):
    help = (
        "Finds potential duplicates of companies in DB and "
        "stores them as tasks for manual resolution"
    )

    ignore_chars = re.escape(":-.)(\",'№«»")

    def cleanup(self, s):
        return re.sub("[\s%s]" % self.ignore_chars, "", s or "")

    def cleanup_digits(self, s):
        return re.sub("[\s%s\d]" % self.ignore_chars, "", s or "")

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        all_companies = []

        keys = ["pk", "code", "name", "name_en", "short_name", "short_name_en"]

        for p in Company.objects.all():
            all_companies.append(
                dict(
                    zip(
                        keys,
                        [
                            p.pk,
                            p.edrpou,
                            p.name_uk,
                            p.name_en,
                            p.short_name_uk,
                            p.short_name_en,
                        ],
                    )
                )
            )

        grouped_by_code = defaultdict(list)
        grouped_by_name = defaultdict(list)

        # First pass: exact matches by code, full name or short name
        for l in all_companies:
            code = self.cleanup(l["code"])
            if len(code) > 2:
                grouped_by_code[code].append(l["pk"])

            for k in ["name", "name_en", "short_name", "short_name_en"]:
                name = self.cleanup(l[k])

                if len(name) > 3:
                    grouped_by_name[name].append(l["pk"])

        spoiled_ids = set()
        chunks_to_review = list()

        for k, v in grouped_by_code.items():
            if len(set(v)) > 1:
                spoiled_ids |= set(v)
                chunks_to_review.append(v)

        for k, v in grouped_by_name.items():
            if len(set(v)) > 1:
                spoiled_ids |= set(v)
                chunks_to_review.append(v)

        for chunk in chunks_to_review:
            try:
                CompanyDeduplication(
                    company1_id=chunk[0],
                    company2_id=chunk[1],
                    company1_json=Company.objects.get(pk=chunk[0]).to_dict(),
                    company2_json=Company.objects.get(pk=chunk[1]).to_dict(),
                ).save()
            except IntegrityError:
                pass

        candidates_for_fuzzy = [l for l in all_companies if l["pk"] not in spoiled_ids]

        for a, b in combinations(candidates_for_fuzzy, 2):
            for field_a, field_b in product(["name", "short_name"], repeat=2):
                val_a = self.cleanup(a[field_a])
                val_b = self.cleanup(b[field_b])
                if len(val_a) < 4 or len(val_b) < 4:
                    continue

                if self.cleanup_digits(a[field_a]) == self.cleanup_digits(b[field_b]):
                    continue

                score = jaro(val_a, val_b)
                if score > 0.97:
                    try:
                        CompanyDeduplication(
                            company1_id=a["pk"],
                            company2_id=b["pk"],
                            company1_json=Company.objects.get(pk=a["pk"]).to_dict(),
                            company2_json=Company.objects.get(pk=b["pk"]).to_dict(),
                            fuzzy=True,
                        ).save()
                        break
                    except IntegrityError:
                        pass

            for field_a, field_b in product(["name_en", "short_name_en"], repeat=2):
                val_a = self.cleanup(a[field_a])
                val_b = self.cleanup(b[field_b])
                if len(val_a) < 4 or len(val_b) < 4:
                    continue

                if self.cleanup_digits(a[field_a]) == self.cleanup_digits(b[field_b]):
                    continue

                score = jaro(val_a, val_b)

                if score > 0.97:
                    try:
                        CompanyDeduplication(
                            company1_id=a["pk"],
                            company2_id=b["pk"],
                            company1_json=Company.objects.get(pk=a["pk"]).to_dict(),
                            company2_json=Company.objects.get(pk=b["pk"]).to_dict(),
                            fuzzy=True,
                        ).save()
                        break
                    except IntegrityError:
                        pass
