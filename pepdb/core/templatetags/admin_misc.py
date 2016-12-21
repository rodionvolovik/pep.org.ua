# coding: utf-8
from __future__ import unicode_literals
from django import template

from core.models import Person
register = template.Library()


@register.filter
def suggest(person):
    """
    Search DB for existing users.
    """
    res = Person.objects.filter(
        last_name_uk__iexact=person["last_name"].lower(),
        first_name_uk__istartswith=person["first_name"].strip(".")[:1].lower(),
        patronymic_uk__istartswith=person["patronymic"].strip(".")[:1].lower()
    )

    return res
