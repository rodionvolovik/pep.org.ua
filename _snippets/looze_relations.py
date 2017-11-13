from core.models import Person2Person
from django.db.models import Q


for r in Person2Person.objects.filter(Q(from_relationship_type__icontains="/") | Q(to_relationship_type__icontains="/")):
    print(r)
