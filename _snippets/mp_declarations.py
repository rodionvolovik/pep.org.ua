res = []
for p2c in Person2Company.objects.filter(to_company_id=63).prefetch_related("from_person"):
    for d in Declaration.objects.filter(nacp_declaration=True, person=p2c.from_person, confirmed="a").order_by("year"):
        res.append({
            "name": p2c.from_person.full_name,
            "year": d.year,
            "id": d.declaration_id.replace("nacp_", "", 1)
        })


 with open("/tmp/mp_decls.csv", "w") as fp:
     from unicodecsv import DictWriter
     w = DictWriter(fp, fieldnames=res[0].keys())
     w.writerows(res)