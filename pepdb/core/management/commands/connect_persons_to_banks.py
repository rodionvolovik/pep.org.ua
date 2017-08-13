# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date
from django.core.management.base import BaseCommand
from collections import defaultdict
from unicodecsv import DictReader

from core.model.exc import CannotResolveRelativeException
from core.models import Company, Person2Company, Declaration, Person


class Command(BaseCommand):
    def find_bank(self, edrpou, name):
        if edrpou:
            if edrpou in self.edrpous_mapping:
                return [self.banks_dict[
                    self.edrpous_mapping[self.edrpous_mapping[edrpou]]
                ]]

        if name in self.names_mapping:
            return [
                self.banks_dict[code]
                for code in self.names_mapping[name]
            ]

        stripped_name = name.strip('"\'')
        if stripped_name in self.names_mapping:
            return [
                self.banks_dict[code]
                for code in self.names_mapping[stripped_name]
            ]

        self.stderr.write(
            "Cannot find bank %s (%s) in mapping" % (name, edrpou)
        )

        return None

    def handle(self, *args, **options):
        self.banks_dict = {}
        self.edrpous_mapping = {}
        self.names_mapping = defaultdict(set)

        # Reading mapping between edrpous of bank branches and
        # edrpou of main branch of the bank
        with open("core/dicts/bank_edrpous_mapping.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                self.edrpous_mapping[bank["edrpou_branch"]] = bank["edrpou_base"]

        # Reading mapping between names of bank and it's edrpous
        with open("core/dicts/bank_names_mapping.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                self.names_mapping[bank["name"]].add(bank["edrpou"])
                self.names_mapping[bank["name"].strip('"\'')].add(bank["edrpou"])

        with open("core/dicts/true_banks.csv", "r") as fp:
            r = DictReader(fp)

            for bank in r:
                if bank["edrpou"]:
                    edrpou = bank["edrpou"]
                    try:
                        self.banks_dict[edrpou] = Company.objects.get(edrpou=edrpou.rjust(8, "0"))
                    except Company.DoesNotExist:
                        self.stderr.write("Cannot find bank with edrpou %s" % edrpou) 
                else:
                    self.stderr.write("Bank %s has no edrpou" % bank["name"])

        successful = 0
        failed = 0
        created = 0
        updated = 0
        for d in Declaration.objects.filter(nacp_declaration=True, confirmed="a"):
            data = d.source["nacp_orig"]

            if isinstance(data.get("step_12"), dict):
                for cash_rec in data["step_12"].values():
                    if not isinstance(cash_rec, dict):
                        continue

                    rec_type = cash_rec.get("objectType", "").lower()
                    person = d.person

                    if cash_rec.get("person", "1") != "1":
                        try:
                            person = d.resolve_person(cash_rec.get("person"))
                        except CannotResolveRelativeException as e:
                            self.stderr.write(unicode(e))

                    if rec_type == "кошти, розміщені на банківських рахунках":
                        bank_name = cash_rec.get("organization_ua_company_name") or \
                            cash_rec.get("organization_ukr_company_name", "")

                        bank_edrpou = cash_rec.get("organization_ua_company_code", "")

                        bank_name = bank_name.lower().strip()
                        bank_edrpou = bank_edrpou.lstrip("0").strip()

                        if bank_name or bank_edrpou:
                            bank_matches = self.find_bank(bank_edrpou, bank_name)
                            if bank_matches is None:
                                failed += 1
                                continue

                            for bank in bank_matches:
                                conns = Person2Company.objects.filter(
                                    from_person=person,
                                    to_company=bank,
                                    relationship_type="Клієнт")

                                last_day_of_year = date(int(d.year), 12, 31)
                                if conns.count():
                                    conn = conns[0]

                                    updated += 1
                                    if conn.date_confirmed:
                                        if last_day_of_year > conn.date_confirmed:
                                            conn.date_confirmed_details = 0
                                            conn.date_confirmed = last_day_of_year
                                    else:
                                        conn.date_confirmed_details = 0
                                        conn.date_confirmed = last_day_of_year
                                else:
                                    created += 1
                                    conn = Person2Company(
                                        from_person=person,
                                        to_company=bank,
                                        relationship_type="Клієнт",
                                        date_confirmed_details=0,
                                        date_confirmed=last_day_of_year,
                                    )

                                conn.declarations = list(
                                    set(conn.declarations or []) |
                                    set([d.pk])
                                )

                                conn.proof_title = ", ".join(filter(None,
                                    set(conn.proof_title.split(", ")) |
                                    set(["Декларація за %s рік" % d.year])
                                ))

                                conn.proof = ", ".join(filter(None,
                                    set(conn.proof.split(", ")) |
                                    set([d.url + "?source"])
                                ))

                                conn.save()

                            successful += 1

        self.stdout.write(
            "Mapping failed: %s, mapping successful: %s" % (failed, successful)
        )
        self.stdout.write(
            "Connections created: %s, connections updated: %s" %
            (created, updated)
        )
