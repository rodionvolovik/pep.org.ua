# coding: utf-8
from __future__ import unicode_literals
from django import template

from elasticsearch_dsl.query import Q
from core.elastic_models import Person as ElasticPerson
from core.models import Person
register = template.Library()


@register.filter
def suggest(person):
    """
    Searches DB for existing users
    """

    res = Person.objects.filter(
        last_name_uk__iexact=person["last_name"].lower(),
        first_name_uk__istartswith=person["first_name"].strip(".")[:4].lower(),
        patronymic_uk__istartswith=person["patronymic"].strip(".")[:4].lower()
    )

    return res
