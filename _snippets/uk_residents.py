from unicodecsv import DictWriter
from core.models import Company2Country

countries_list = [
    "Велика Британія",
    "Британські Віргінські Острови",
    "Гібралтар",
    "Бермудські острови",
    "Кайманові острови",
    "Гернсі",
    "Джерсі",
    "Острів Мен"
]


with open("/tmp/uk_companies.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=["country", "company_name", "company_code", "company_url", "founders", "managers", "rest", "sanctions"])
    w.writeheader()
    for c2c in Company2Country.objects.filter(to_country__name_uk__in=countries_list).select_related("to_country"):
        related = c2c.from_company.all_related_persons

        def joiner(persons):
            return u"\n".join([u"{}, https://pep.org.ua/{}".format(p.full_name, p.get_absolute_url()) for p in persons])

        w.writerow({
            "country": c2c.to_country.name_uk,
            "company_name": c2c.from_company.name_uk,
            "company_code": c2c.from_company.edrpou,
            "company_url": "https://pep.org.ua/{}".format(c2c.from_company.get_absolute_url()),
            "founders": joiner(related["founders"]),
            "managers": joiner(related["managers"]),
            "rest": joiner(related["rest"]),
            "sanctions": joiner(related["sanctions"]),
        })