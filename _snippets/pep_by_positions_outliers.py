from tasks.management.commands.monitor_edr import Command as helper

from django.db.models.functions import Lower
from elasticsearch_dsl import Q
from core.models import Person2Company, Person

q = Person2Company.objects.select_related("to_company", "from_person") \
    .filter(from_person__is_pep=True, to_company__state_company=True) \
    .annotate(rt_lower=Lower("relationship_type_uk")) \
    .exclude(rt_lower__in=helper.positions_to_monitor + ("клієнт банку", ))

with open("weird_positioned_peps.csv", "w") as fp:
    w = writer(fp)
    for p in q:
        w.writerow([p.from_person.get_absolute_url(), p.from_person.full_name, p.relationship_type_uk, p.to_company.name_uk])


from core.models import Person2Company, Person
from django.db.models import Count

q = Person.objects.filter(is_pep=True) \
    .annotate(num_state_companies=Count("person2company__to_company", distinct=True, filter=Q(person2company__to_company__state_company=True))) \
    .filter(num_state_companies=0)


with open("peps_with_no_position.csv", "w") as fp:
    w = writer(fp)
    for p in q:
        w.writerow([p.get_absolute_url(), p.full_name])


q = Person.objects.filter(type_of_official=1, is_pep=False) \
    .annotate(num_state_companies=Count("person2company__to_company", distinct=True, filter=Q(person2company__to_company__state_company=True))) \
    .filter(num_state_companies=0)


Person.objects.filter(is_pep=True, type_of_official__isnull=True).count()
Person.objects.filter(is_pep=False, type_of_official__in=[1, 2, 3]).count()