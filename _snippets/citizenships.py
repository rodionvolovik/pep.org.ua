from unicodecsv import DictWriter
from tasks.constants import COUNTRIES as countries

res = []
from core.models import Declaration

for d in Declaration.objects.filter(confirmed="a", nacp_declaration=True).nocache().iterator():
    step_1 = d.source["nacp_orig"].get("step_1", {})
    step_2 = d.source["nacp_orig"].get("step_2", {})
    for s2 in step_2.values():
        if not isinstance(s2, dict):
            continue
        if s2.get("citizenship") and s2.get("citizenship") != "1":
            res.append({
                "person": d.person_id,
                "first_name": d.first_name,
                "patronymic": d.patronymic,
                "last_name": d.last_name,
                "relative_first_name": s2.get("firstname", ""),
                "relative_patronymic": s2.get("middlename", ""),
                "relative_last_name": s2.get("lastname", ""),
                "citizenship": countries.get(s2.get("citizenship")),
            })

with open("/tmp/foreigners.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=res[0].keys())
    w.writeheader()
    w.writerows(res)