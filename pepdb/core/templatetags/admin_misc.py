# coding: utf-8
from __future__ import unicode_literals
from django import template

from core.models import Person, Person2Person

register = template.Library()


@register.filter
def suggest(person, parent_id):
    """
    Search DB for existing users.
    """

    parent_id = int(parent_id)
    last_name = person["last_name"].lower()
    first_name = person["first_name"].strip(".")[:1].lower()
    patronymic = person["patronymic"].strip(".")[:1].lower()

    possible_relations = []
    used_ids = []

    rel1 = Person2Person.objects.select_related("from_person").filter(
        from_person_id=parent_id,
        to_person__last_name_uk__iexact=last_name,
        to_person__first_name_uk__istartswith=first_name,
        to_person__patronymic_uk__istartswith=patronymic,
    )

    for rel in rel1:
        used_ids.append(rel.to_person_id)
        possible_relations.append(
            {
                "subject": rel.to_person,
                "from": rel.from_relationship_type,
                "rel_id": rel.pk,
                "reverse": False,
                "to": rel.to_relationship_type,
            }
        )

    rel2 = Person2Person.objects.select_related("to_person").filter(
        to_person_id=parent_id,
        from_person__last_name_uk__iexact=last_name,
        from_person__first_name_uk__istartswith=first_name,
        from_person__patronymic_uk__istartswith=patronymic,
    )

    for rel in rel2:
        used_ids.append(rel.from_person_id)
        possible_relations.append(
            {
                "subject": rel.from_person,
                "rel_id": rel.pk,
                "from": rel.to_relationship_type,
                "reverse": True,
                "to": rel.from_relationship_type,
            }
        )

    res = Person.objects.filter(
        last_name_uk__iexact=last_name,
        first_name_uk__istartswith=first_name,
        patronymic_uk__istartswith=patronymic,
    )

    for pers in res:
        if pers.id in used_ids:
            continue

        possible_relations.append({"subject": pers})

    return possible_relations
