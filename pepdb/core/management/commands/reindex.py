# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Company, Person
from core.elastic_models import (
    Person as ElasticPerson,
    Company as ElasticCompany
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        ElasticPerson.init()
        counter = 0
        for p in Person.objects.all():
            item = ElasticPerson(**p.to_dict())
            item.save()
            counter += 1

        self.stdout.write(
            'Loaded {} persons to persistence storage'.format(counter))

        ElasticCompany.init()
        counter = 0
        for p in Company.objects.all():
            item = ElasticCompany(**p.to_dict())
            item.save()
            counter += 1

        self.stdout.write(
            'Loaded {} companies to persistence storage'.format(counter))
