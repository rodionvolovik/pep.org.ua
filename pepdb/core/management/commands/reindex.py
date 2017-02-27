# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from elasticsearch_dsl import Index
from elasticsearch.helpers import streaming_bulk
from elasticsearch_dsl.connections import connections

from core.models import Company, Person
from core.elastic_models import (
    Person as ElasticPerson,
    Company as ElasticCompany
)


class Command(BaseCommand):
    def bulk_write(self, conn, docs_to_index):
        for response in streaming_bulk(
                conn, (d.to_dict(True) for d in docs_to_index)):
            pass

    def handle(self, *args, **options):
        conn = connections.get_connection('default')

        Index(ElasticPerson._doc_type.index).delete(ignore=404)
        ElasticPerson.init()
        conn.indices.put_settings(
            index=ElasticPerson._doc_type.index,
            body={
                'index.max_result_window': 100000
            }
        )

        docs_to_index = [
            ElasticPerson(**p.to_dict())
            for p in Person.objects.all()]

        self.bulk_write(conn, docs_to_index)

        self.stdout.write(
            'Loaded {} persons to persistence storage'.format(
                len(docs_to_index)))

        ElasticCompany.init()
        conn.indices.put_settings(
            index=ElasticCompany._doc_type.index,
            body={
                'index.max_result_window': 100000
            }
        )

        docs_to_index = [
            ElasticCompany(**p.to_dict())
            for p in Company.objects.all()]

        self.bulk_write(conn, docs_to_index)

        self.stdout.write(
            'Loaded {} companies to persistence storage'.format(
                len(docs_to_index)))
