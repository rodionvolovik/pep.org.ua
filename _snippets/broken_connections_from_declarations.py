import unicodecsv
from core.models import Person2Company, Declaration

if __name__ == '__main__':

    with open("/tmp/outdated_links.csv", "w") as fp:
        w = unicodecsv.DictWriter(fp, fieldnames=["person", "connection", "relation", "last_declaration"])
        w.writeheader()

        for p2c in Person2Company.objects.all().nocache().iterator():
            if not p2c.date_finished and p2c.declarations:
                declaration_years = Declaration.objects.filter(
                    pk__in = p2c.declarations
                ).values_list("year", flat=True)
                max_year = max(map(int, declaration_years))
                if max_year < 2018:
                    w.writerow({
                        "person": p2c.from_person,
                        "connection": p2c.to_company,
                        "relation": p2c.relationship_type_uk,
                        "last_declaration": max_year
                    })
