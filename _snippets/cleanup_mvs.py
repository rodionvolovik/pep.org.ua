from collections import Counter
from tasks.models import AdHocMatch

for m in AdHocMatch.objects.filter(dataset_id="wanted_ia").nocache().iterator():
    AdHocMatch.objects.filter(
            dataset_id="wanted_ia_new",
            person=m.person,
            matched_json__FIRST_NAME__iexact=m.matched_json["FIRST_NAME"],
            matched_json__LAST_NAME__iexact=m.matched_json["LAST_NAME"],
            matched_json__MIDDLE_NAME__iexact=m.matched_json["MIDDLE_NAME"],
            matched_json__BIRTH_DATE__iexact=m.matched_json["BIRTH_DATE"]
        ).update(status="i")