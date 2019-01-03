from core.models import Person
from tqdm import tqdm
from unicodecsv import writer
from django.conf import settings

if __name__ == "__main__":
    q = Person.objects.filter(type_of_official=1, reason_of_termination__isnull=True)

    with open("/tmp/incomplete_declarations.csv", "w") as fp:
        w = writer(fp)

        for p in tqdm(
            q.nocache().iterator(),
            total=q.count()
        ):
            decls_list = p.declarations.filter(nacp_declaration=True, confirmed="a").distinct("year").values_list("year", flat=True)

            if decls_list and len(decls_list) < 3 and list(decls_list) != ["2016", "2017"]:
                w.writerow([p.full_name, settings.SITE_URL + p.get_absolute_url(), ",".join(decls_list)])
