import unicodecsv
from core.models import Person2Company, Declaration

if __name__ == "__main__":

    with open("/tmp/outdated_links.csv", "w") as fp:
        w = unicodecsv.DictWriter(
            fp,
            fieldnames=[
                "person",
                "url",
                "connection",
                "relation",
                "last_declaration_for_connection",
                "last_declaration_of_person",
                "has_newer_declarations",
            ],
        )
        w.writeheader()

        for p2c in (
            Person2Company.objects.select_related("from_person", "to_company")
            .nocache()
            .iterator()
        ):
            if not p2c.date_finished and p2c.declarations:
                declaration_years = Declaration.objects.filter(
                    pk__in=p2c.declarations, confirmed="a"
                ).values_list("year", flat=True)
                max_year = max(map(int, declaration_years))

                if max_year < 2018:
                    person_declaration_years = Declaration.objects.filter(
                        person=p2c.from_person, confirmed="a"
                    ).values_list("year", flat=True)

                    person_declaration_years = list(
                        filter(None, person_declaration_years)
                    )
                    if person_declaration_years:
                        max_person_declaration_year = max(
                            map(int, person_declaration_years)
                        )
                    else:
                        max_person_declaration_year = ""

                    w.writerow(
                        {
                            "person": p2c.from_person,
                            "url": "https://pep.org.ua{}".format(
                                p2c.from_person.get_absolute_url()
                            ),
                            "connection": p2c.to_company,
                            "relation": p2c.relationship_type_uk,
                            "last_declaration_for_connection": max_year,
                            "last_declaration_of_person": max_person_declaration_year,
                            "has_newer_declarations": (
                                max_year != max_person_declaration_year
                            )
                            and bool(max_person_declaration_year),
                        }
                    )
