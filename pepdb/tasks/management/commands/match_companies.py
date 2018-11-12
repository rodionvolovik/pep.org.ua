# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.conf import settings

from elasticsearch_dsl import Q

from core.models import Company, Person2Company
from tasks.elastic_models import EDRPOU
from tasks.models import CompanyMatching


class Command(BaseCommand):
    help = (
        "Find candidates for matching between companies in DB and "
        "companies from state registry, loaded in search index"
    )

    def search_me(self, company, fuzziness=1, candidates=10):
        if company["edrpou"]:
            res = EDRPOU.search().query("term", edrpou=company["edrpou"].lstrip("0"))
        else:
            should = [
                Q("match", location={"query": company["city"], "fuzziness": fuzziness}),
                Q(
                    "multi_match",
                    query="%s %s" % (company["name_uk"], company["short_name_uk"]),
                    fuzziness=fuzziness,
                    fields=["name", "short_name", "location"],
                    boost=1.5,
                ),
            ]

            for headname in company["heads"]:
                should.append(
                    Q(
                        "match",
                        head={
                            "query": headname,
                            "operator": "or",
                            "minimum_should_match": 3,
                            "fuzziness": fuzziness,
                        },
                    )
                )

            res = (
                EDRPOU.search()
                .query(Q("bool", should=should))
                .highlight_options(
                    order="score",
                    fragment_size=500,
                    number_of_fragments=100,
                    pre_tags=['<u class="match">'],
                    post_tags=["</u>"],
                )
                .highlight("name", "head", "short_name", "location")
            )

        ans = res.execute()
        res = []
        for a in ans[:candidates]:
            highlight = getattr(a.meta, "highlight", {})

            name = " ".join(a.meta.highlight.name) if "name" in highlight else a.name
            short_name = (
                " ".join(a.meta.highlight.short_name)
                if "short_name" in highlight
                else a.short_name
            )
            head = " ".join(a.meta.highlight.head) if "head" in highlight else a.head
            location = (
                " ".join(a.meta.highlight.location)
                if "location" in highlight
                else a.location
            )

            res.append(
                {
                    "name": name,
                    "short_name": short_name,
                    "head": head,
                    "location": location,
                    "edrpou": a.edrpou,
                    "status": a.status,
                    "company_profile": a.company_profile,
                    "score": a._score,
                }
            )

        return res

    def handle(self, *args, **options):
        for company in Company.objects.values(
            "id", "short_name_uk", "name_uk", "edrpou", "city"
        ):
            company["heads"] = [
                " ".join(x)
                for x in Person2Company.objects.filter(to_company_id=company["id"])
                .select_related("from_person")
                .values_list(
                    "from_person__last_name",
                    "from_person__first_name",
                    "from_person__patronymic",
                )
            ]

            candidates = self.search_me(company)

            # TODO: check if task already exists and not solved yet
            CompanyMatching(
                company_json=company,
                candidates_json=candidates,
                company_id=company["id"],
            ).save()
