res = []
from core.models import Declaration

for d in Declaration.objects.filter(confirmed="a", nacp_declaration=True).prefetch_related("person").nocache():
    step_11 = d.source["nacp_orig"].get("step_11", {})
    step_2 = d.source["nacp_orig"].get("step_2", {})

    for income_rec in step_11.values():
        if not isinstance(income_rec, dict):
            continue

        declarant = ""
        if income_rec.get("person", "1") == "1":
            declarant = d.person.full_name
        else:
            if isinstance(step_2, dict) and income_rec["person"] in step_2:
                fam = step_2[income_rec["person"]]
                if isinstance(fam, dict):
                    declarant = " ".join([fam.get("lastname", ""), fam.get("firstname", ""), fam.get("middlename", "")])

        res.append({
            "Тип доходу": income_rec.get("otherObjectType") or income_rec.get("objectType"),
            "Розмір": income_rec.get("sizeIncome"),
            "Від": income_rec.get("source_citizen"),
            "Від (назва)": income_rec.get("source_ua_company_name"),
            "Від (код)": income_rec.get("source_ua_company_code"),
            "Декларує": declarant,
            "Декларує (тип)": "Декларант" if income_rec.get("person", "1") == "1" else "Член родини",
            "Рік": d.year,
            "Посилання на декларацію": d.url,
            "Посилання на профіль ПЕП": d.person.get_absolute_url(),
        })
