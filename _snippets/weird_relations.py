from core.models import Person2Person

for p2p in Person2Person.objects.all():
    if p2p.from_relationship_type not in Person2Person._relationships_explained.get(p2p.to_relationship_type, []):
        print(p2p)
