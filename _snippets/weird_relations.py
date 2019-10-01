from core.models import Person2Person, Person

fem = [
    "дружина",
    "мати",
    "дочка",
    "мачуха",
    "падчерка",
    "рідна сестра",
    "баба",
    "прабаба",
    "внучка",
    "правнучка",
    "невістка",
    "теща",
    "свекруха",
]

masc = [
   "чоловік",
   "батько",
   "син",
   "вітчим",
   "пасинок",
   "рідний брат",
   "дід",
   "прадід",
   "внук",
   "правнук",
   "зять",
   "тесть",
   "свекор",
]


for p2p in Person2Person.objects.all().nocache().iterator():
    if p2p.from_relationship_type not in Person2Person._relationships_explained.get(
        p2p.to_relationship_type, []
    ):
        print(p2p)

    if p2p.from_relationship_type == "" or p2p.to_relationship_type == "":
        print(p2p)

masc_from = set(Person2Person.objects.filter(from_relationship_type__in=masc).values_list("from_person_id", flat=True).nocache())
masc_to = set(Person2Person.objects.filter(to_relationship_type__in=masc).values_list("to_person_id", flat=True).nocache())
fem_from = set(Person2Person.objects.filter(from_relationship_type__in=fem).values_list("from_person_id", flat=True).nocache())
fem_to = set(Person2Person.objects.filter(to_relationship_type__in=fem).values_list("to_person_id", flat=True).nocache())


for person in Person.objects.filter(pk__in=(masc_from | masc_to) & (fem_from | fem_to)):
    print("{} {}".format(person, person.pk))
