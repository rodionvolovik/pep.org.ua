from datetime import date
from unicodecsv import DictWriter
from tqdm import tqdm
from tasks.models import SMIDACandidate
from core.utils import ceil_date, floor_date
from core.models import Person2Company, Person2Person, Company

smida_companies = list(SMIDACandidate.objects.filter(status="a").values_list("smida_edrpou", flat=True).distinct())

with open("/tmp/strange_connections.csv", "w") as fp:
    w = DictWriter(fp, fieldnames=["company", "person1", "person2", "p1_to_p2", "p1_to_c", "p2_to_c", "p1_from", "p1_to", "p2_from", "p2_to"])
    w.writeheader()

    for edrpou in tqdm(smida_companies):
        company = Company.objects.filter(edrpou__in=[edrpou, edrpou.lstrip("0"), unicode(edrpou).rjust(8, "0")]).first()

        personnel = {}
        for p2c in Person2Company.objects.filter(to_company_id=company.pk):
            personnel[p2c.from_person_id] = p2c


        for p2p in Person2Person.objects.filter(from_person_id__in=personnel.keys(), to_person_id__in=personnel.keys()).select_related("from_person", "to_person"):
            dates_1 = [floor_date(personnel[p2p.from_person_id].date_established, personnel[p2p.from_person_id].date_established_details), 
                ceil_date(personnel[p2p.from_person_id].date_finished, personnel[p2p.from_person_id].date_finished_details)]

            dates_2 = [floor_date(personnel[p2p.to_person_id].date_established, personnel[p2p.to_person_id].date_established_details), 
                ceil_date(personnel[p2p.to_person_id].date_finished, personnel[p2p.to_person_id].date_finished_details)]

            if dates_1[0] is None:
                dates_1[0] = date(1991, 1, 1)

            if dates_2[0] is None:
                dates_2[0] = date(1991, 1, 1)

            if dates_1[1] is None:
                dates_1[1] = date.today()

            if dates_2[1] is None:
                dates_2[1] = date.today()


            overlap = (dates_1[0] <= dates_2[1] and dates_2[0] <= dates_1[1])

            if not overlap:
                w.writerow({
                    "company": company,
                    "person1": p2p.from_person,
                    "person2": p2p.to_person,
                    "p1_to_p2": p2p.from_relationship_type,
                    "p1_to_c": personnel[p2p.from_person_id].relationship_type_uk,
                    "p2_to_c": personnel[p2p.to_person_id].relationship_type_uk,
                    "p1_from": dates_1[0],
                    "p1_to": dates_1[1],
                    "p2_from": dates_2[0],
                    "p2_to": dates_2[1],
                })

                p2p.delete()
