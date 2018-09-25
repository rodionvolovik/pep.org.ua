# coding: utf-8
from __future__ import unicode_literals
import sys

from collections import defaultdict
from unicodecsv import DictReader, DictWriter
from core.models import Company
from django.conf import settings

fieldnames = "date_of_report,EDRPOU,emitent_name,ICIH,owner_edrpou,last_name,first_name,patronymic,foreign_code,type_of_stock,nominal_price,share,number_of_shares,country_code".split(",")

smida_records = defaultdict(list)
smida_owner_records = defaultdict(list)
smida_indirect_records = defaultdict(list)
with open("/tmp/owners_2018_q1_renamed.csv", "r") as fp:
    r = DictReader(fp)

    for l in r:
        smida_records[l["EDRPOU"].strip().lstrip("0")].append(l)
        smida_owner_records[l["owner_edrpou"].strip().lstrip("0")].append(l)


with open("/tmp/coowned_by_state.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=["pep_company_name", "pep_company_link"] + fieldnames)

    w.writeheader()
    coowned_by_state = 0
    for c in Company.objects.filter(state_company=True).nocache().iterator():
        edrpou = c.edrpou.lstrip("0")
        if edrpou and edrpou in smida_owner_records:
            coowned_by_state += 1
            for l in smida_owner_records[edrpou]:
                rec = l.copy()
                rec["pep_company_name"] = c.name_uk
                rec["pep_company_link"] = u"{}{}".format(settings.SITE_URL, c.get_absolute_url())
                smida_indirect_records[l["EDRPOU"].strip().lstrip("0")].append(rec)

                w.writerow(rec)

    print("Coowned by state: {}".format(coowned_by_state))


with open("/tmp/coowned_indirectly_by_state.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=["pep_company_name", "pep_company_link"] + fieldnames)

    w.writeheader()
    coowned_indirectly_by_state = 0
    for edrpou in smida_indirect_records:
        coowned_indirectly_by_state += 1
        for l in smida_indirect_records[edrpou]:
            w.writerow(l)

    print("Coowned indirectly by state: {}".format(coowned_indirectly_by_state))


with open("/tmp/state_companies.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=["pep_company_name", "pep_company_link"] + fieldnames)

    w.writeheader()
    state_companies = 0
    for c in Company.objects.filter(state_company=True).nocache().iterator():
        edrpou = c.edrpou.lstrip("0")
        if edrpou and edrpou in smida_records:
            state_companies += 1
            for l in smida_records[edrpou]:
                rec = l.copy()
                rec["pep_company_name"] = c.name_uk
                rec["pep_company_link"] = u"{}{}".format(settings.SITE_URL, c.get_absolute_url())

                w.writerow(rec)

    print("Owned by state: {}".format(state_companies))
