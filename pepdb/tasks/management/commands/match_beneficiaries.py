# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import json

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings
from django.db.models import Q as dbQ

from elasticsearch_dsl import Q

from core.models import Declaration, Country, Person, Company
from core.model.exc import CannotResolveRelativeException
from tasks.elastic_models import EDRPOU
from tasks.models import BeneficiariesMatching
from tasks.constants import COUNTRIES


class Command(BaseCommand):
    help = """
    Collect companies where pep persons are beneficiary owners, clean it up,
    reconcile with companies registry, create tasks for manual verification
    """

    def _search_db(self, company):
        try:
            # Search by code first
            company_db = Company.objects.deep_get([
                ("edrpou__iexact", company["beneficial_owner_company_code"]),
                ("edrpou__iexact", (company["beneficial_owner_company_code"] or "").replace(" ", "")),
            ])
        except (Company.DoesNotExist, Company.MultipleObjectsReturned):
            try:
                # Then refine the search if needed
                company_db = Company.objects.deep_get([
                    ("name_uk__iexact", company["company_name"]),
                    ("name_uk__iexact", company["en_name"]),
                    ("name_en__iexact", company["company_name"]),
                    ("name_en__iexact", company["en_name"])
                ])

            except Company.DoesNotExist:
                return None
            except Company.MultipleObjectsReturned:
                self.stderr.write(
                    "Too much companies returned for record '%s'" % json.dumps(
                        company, ensure_ascii=False)
                )
                return None

        return {
            "id": company_db.id,
            "code": company_db.edrpou,
            "name_uk": company_db.name_uk,
            "name_en": company_db.name_en,
        }

    def _search_edr(self, company, fuzziness):
        ans = None
        if company["beneficial_owner_company_code"]:
            res = EDRPOU.search().query(
                "term",
                edrpou=company["beneficial_owner_company_code"].lstrip("0")
            )
            ans = res.execute()
            if not ans:
                self.stdout.write(
                    "Cannot find a company by code %s, falling back to search by name %s" %
                    (
                        company["beneficial_owner_company_code"],
                        company["company_name"]
                    )
                )

        if not ans:
            should = [
                Q(
                    "multi_match",
                    query=company["company_name"],
                    fuzziness=fuzziness,
                    fields=["name", "short_name", "location"],
                    boost=2.
                )
            ]

            if company["address"]:
                should.append(
                    Q(
                        "match",
                        location={
                            "query": company["address"],
                            "fuzziness": fuzziness
                        }
                    )
                )

            res = EDRPOU.search() \
                .query(Q("bool", should=should)) \
                .highlight_options(
                    order='score',
                    fragment_size=500,
                    number_of_fragments=100,
                    pre_tags=['<u class="match">'], post_tags=["</u>"]) \
                .highlight("name", "short_name", "location")

            ans = res.execute()

        return ans

    def search_me(self, ownership, fuzziness=1, candidates=10):
        matches = []
        edrpous_found = []
        ids_found = []

        for company in ownership.pep_company_information:
            # For foreign companies we are searching in PEP database itself
            # for those records that has been imported manually

            if company["country"] != "Україна":
                # Totally different logic of search
                rec = self._search_db(company)

                if rec and rec["id"] not in ids_found:
                    matches.append(rec)
                    ids_found.append(rec["id"])
            else:
                # For ukrainian companies we are searching for the information
                # in our local copy of public EDR
                ans = self._search_edr(company, fuzziness)

                for a in ans[:candidates]:
                    highlight = getattr(a.meta, "highlight", {})

                    name = " ".join(a.meta.highlight.name) \
                        if "name" in highlight else a.name
                    short_name = " ".join(a.meta.highlight.short_name) \
                        if "short_name" in highlight else a.short_name
                    location = " ".join(a.meta.highlight.location) \
                        if "location" in highlight else a.location

                    rec = {
                        "name": name,
                        "short_name": short_name,
                        "location": location,

                        "head": a.head,
                        "edrpou": a.edrpou,
                        "status": a.status,
                        "company_profile": a.company_profile,
                        "score": a._score
                    }

                if rec["edrpou"] not in edrpous_found:
                    matches.append(rec)
                    edrpous_found.append(rec["edrpou"])

        return matches[:candidates]

    def resolve_person(self, declaration, ownership):
        try:
            person, _ = declaration.resolve_person(
                ownership.get("person"))
            return person.pk
        except CannotResolveRelativeException as e:
            self.stderr.write(unicode(e))

    def get_key(self, obj, declarant):
        company_name = re.sub(
            "[\s%s]+" % (re.escape("'\"-.,№()")),
            "",
            obj["company_name"].lower(),
            re.U
        )

        return "!!".join((
            declarant.full_name,
            company_name,
        ))

    def insert_record(self, obj, declaration):
        if obj["declarant_id"] is None:
            return

        declarant = Person.objects.get(pk=obj["declarant_id"])
        key = self.get_key(obj, declarant)

        try:
            rec = BeneficiariesMatching.objects.get(company_key=key)

            if obj["country"] != "Україна" and rec.status not in ["y", "n"]:
                self.stderr.write(
                    "Same company %s listed in different sources as domestic and foreign!" % key
                )

        except BeneficiariesMatching.DoesNotExist:
            rec = BeneficiariesMatching(
                company_key=key, pep_company_information=[]
            )

            if obj["country"] != "Україна":
                rec.status = "n"

        rec.person = obj["declarant_id"]
        rec.person_json = declarant.to_dict()
        rec.is_family_member = obj["owner"] == "FAMILY"
        rec.declarations = list(
            set(rec.declarations or []) | set([declaration.pk]))

        if obj not in rec.pep_company_information:
            rec.pep_company_information.append(obj)

        rec.candidates_json = {}
        rec.save()

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)

        self.stdout.write("Retrieving beneficiary ownership information")
        for d in Declaration.objects.filter(
                nacp_declaration=True, confirmed="a").select_related(
                "person"):
            data = d.source["nacp_orig"]
            if isinstance(data.get("step_9"), dict):
                for ownership in data["step_9"].values():
                    if not isinstance(ownership, dict):
                        self.stderr.write("Ownership record '%s' is invalid" % ownership)
                        continue

                    self.insert_record({
                        "declarant_id": (
                            d.person_id if ownership.get("person") == "1"
                            else self.resolve_person(d, ownership)
                        ),
                        "declarant_name": d.person.full_name,
                        "company_name": ownership.get("name"),
                        "legalForm": ownership.get("legalForm"),
                        "country": COUNTRIES[
                            ownership.get("country", "1") or "1"],
                        "en_name": ownership.get("en_name"),
                        "location": ownership.get("location"),
                        "en_address": ownership.get("en_address"),
                        "phone": ownership.get("phone"),
                        "address": ownership.get("address"),
                        "mail": ownership.get("mail"),
                        "year_declared": d.year,
                        "beneficial_owner_company_code": ownership.get(
                            "beneficial_owner_company_code"),
                        "owner": "DECLARANT" if ownership.get(
                            "person") == "1" else "FAMILY"
                    }, declaration=d
                    )

        self.stdout.write("Matching with EDR registry")
        for ownership in BeneficiariesMatching.objects.filter(status__in=["p", "n"]):
            candidates = self.search_me(ownership)
            ownership.candidates_json = candidates

            # corner case for foreign companies: here we found a match
            # for a foreign company in PEP db
            if candidates and ownership.status == "n":
                # So switch status to represent that we've found it
                ownership.status = "y"

            ownership.save()
