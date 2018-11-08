from django.db import models
from unicodecsv import DictWriter
from core.models import Company

fieldnames = ["id", "url", "name", "head_is_pep"]

with open("/tmp/orphaned_companies.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=fieldnames)
    w.writeheader()
    for c in Company.objects.annotate(
            cnt=models.Count("from_persons__from_person", distinct=True, filter=models.Q(from_persons__from_person__is_pep=True))).filter(cnt=0):
        w.writerow({
           "id": c.id,
           "url": "https://pep.org.ua/" + c.get_absolute_url(),
           "name": c.name_uk,
           "head_is_pep": c.state_company
        })