import json
from core.models import Declaration, Company, Person2Company
from django.db.models import Q
from unicodecsv import DictWriter

if __name__ == "__main__":
    fp = open("beneficiary.csv", "w")
    w = DictWriter(fp, fieldnames=["pep", "url", "company_name", "edrpou", "years", "from_declaration", "person_type"], dialect="excel")
    w.writeheader()

    for p2c in (
        Person2Company.objects.filter(Q(relationship_type_uk__icontains=u"Бенеф") | Q(relationship_type_uk__icontains=u"власн"))
        .select_related("to_company", "from_person")
        .exclude(to_company__edrpou="")
    ):
        regs = list(p2c.to_company.foreign_registration.values_list("to_country__name_uk", flat=True))

        if regs and u"Україна" not in regs:
            continue

        years = []
        from_declaration = False
        if p2c.declarations:
            from_declaration = True
            years = set(Declaration.objects.filter(pk__in=p2c.declarations).values_list("year", flat=True))
        else:
            years = map(lambda x: x.year, filter(None, [p2c.date_established, p2c.date_finished, p2c.date_confirmed]))
            if years:
                years = map(unicode, range(min(years), max(years) + 1))

        w.writerow({
            "pep": p2c.from_person.full_name,
            "url": "https://pep.org.ua{}".format(p2c.from_person.get_absolute_url()),
            "company_name": unicode(p2c.to_company),
            "edrpou": p2c.to_company.edrpou,
            "years": ", ".join(sorted(years)),
            "from_declaration": from_declaration,
            "person_type": "owner" if u"бенеф" in p2c.relationship_type_uk.lower() else "founder"
        })