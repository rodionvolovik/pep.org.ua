from unicodecsv import DictWriter
from core.models import Declaration

changes = []

for d in Declaration.objects.filter(confirmed="a", nacp_declaration=True).nocache().iterator():
    step_1 = d.source["nacp_orig"].get("step_1", {})
    step_2 = d.source["nacp_orig"].get("step_2", {})

    for s2 in step_2.values():
        if not isinstance(s2, dict):
            continue
        if s2.get("previous_firstname") or s2.get("previous_lastname") or s2.get("previous_middlename"):
            changes.append({
                "person": d.person_id,
                "first_name": s2.get("firstname", ""),
                "patronymic": s2.get("middlename", ""),
                "last_name": s2.get("lastname", ""),
                "prev_first_name": s2.get("previous_firstname", ""),
                "prev_patronymic": s2.get("previous_middlename", ""),
                "prev_last_name": s2.get("previous_lastname", ""),
            })

    if step_1.get("previous_firstname") or step_1.get("previous_lastname") or step_1.get("previous_middlename"):
        changes.append({
            "person": d.person_id,
            "first_name": d.first_name,
            "patronymic": d.patronymic,
            "last_name": d.last_name,
            "prev_first_name": step_1.get("previous_firstname", ""),
            "prev_patronymic": step_1.get("previous_middlename", ""),
            "prev_last_name": step_1.get("previous_lastname", ""),
        })

with open("/tmp/changed_names.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=changes[0].keys())
    w.writeheader()
    w.writerows(changes)
