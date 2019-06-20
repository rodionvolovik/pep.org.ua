# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
import os.path
from django.core.management.base import BaseCommand, CommandError
from unicodecsv import writer
from core.models import (
    Person, Company, Country, Person2Person, Company2Company,
    Person2Company, Company2Country, Person2Country)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'output_dir',
            help='Directory to export CSVs',
        )

    def norm_str(self, s):
        return re.sub("\s+", " ", unicode(s).replace("\n", " ").strip())

    def export_nodes(self, fname, qs, fields, labels=[]):
        with open(fname, "w") as fp:
            w = writer(fp)
            id_fields = "%sId:ID(%s)" % (
                qs.model.__name__.lower(), qs.model.__name__)

            w.writerow([id_fields] + fields + [":LABEL"])

            for obj in qs:
                w.writerow([
                    getattr(obj, "get_%s_display" % x)()
                    if hasattr(obj, "get_%s_display" % x) else
                    self.norm_str(getattr(obj, x)) for x in ["pk"] + fields
                ] + [";".join(labels)])

    def export_relations(self, fname, qs, src, dst, fields):
        with open(fname, "w") as fp:
            w = writer(fp)
            if_fld_from = getattr(qs.model, src).field.related_model.__name__
            if_fld_to = getattr(qs.model, dst).field.related_model.__name__

            w.writerow(
                [
                    ":START_ID(%s)" % if_fld_from,
                    ":END_ID(%s)" % if_fld_to,
                    ":TYPE"
                ] + fields)

            for obj in qs:
                w.writerow(
                    [
                        getattr(obj, src + "_id"),
                        getattr(obj, dst + "_id"),
                        qs.model.__name__
                    ] +
                    [
                        getattr(obj, "get_%s_display" % x)()
                        if hasattr(obj, "get_%s_display" % x) else
                        self.norm_str(getattr(obj, x)) for x in fields
                    ]
                )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]

        try:
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
        except OSError:
            raise CommandError('Cannot create output dir')

        self.export_nodes(
            os.path.join(output_dir, "persons.csv"),
            Person.objects.all(),
            [
                "full_name",
                "date_of_birth",
                "type_of_official",
                "is_pep",
                "url_uk"
            ],
            ["Person"]
        )

        self.export_nodes(
            os.path.join(output_dir, "companies.csv"),
            Company.objects.all(),
            [
                "name_uk",
                "founded_human",
                "state_company",
                "edrpou",
                "url_uk"
            ],
            ["Company"]
        )

        self.export_nodes(
            os.path.join(output_dir, "countries.csv"),
            Country.objects.exclude(iso2=""),
            [
                "name_uk",
                "iso2",
                "iso3",
                "is_jurisdiction",
                "url_uk"
            ],
            ["Country"]
        )

        self.export_relations(
            os.path.join(output_dir, "person2person.csv"),
            Person2Person.objects.all(),
            "from_person",
            "to_person",
            [
                "from_relationship_type",
                "to_relationship_type",
                "date_established_human",
                "date_finished_human",
                "date_confirmed_human",
                "proof_title",
                "proof",
            ]
        )

        self.export_relations(
            os.path.join(output_dir, "person2company.csv"),
            Person2Company.objects.all(),
            "from_person",
            "to_company",
            [
                "relationship_type",
                "is_employee",
                "date_established_human",
                "date_finished_human",
                "date_confirmed_human",
                "proof_title",
                "proof",
            ]
        )

        self.export_relations(
            os.path.join(output_dir, "company2company.csv"),
            Company2Company.objects.all(),
            "from_company",
            "to_company",
            [
                "relationship_type",
                "reverse_relationship_type",
                "equity_part",
                "date_established_human",
                "date_finished_human",
                "date_confirmed_human",
                "proof_title",
                "proof",
            ]
        )

        self.export_relations(
            os.path.join(output_dir, "person2country.csv"),
            Person2Country.objects.all(),
            "from_person",
            "to_country",
            [
                "relationship_type",
                "date_established_human",
                "date_finished_human",
                "date_confirmed_human",
                "proof_title",
                "proof",
            ]
        )

        self.export_relations(
            os.path.join(output_dir, "company2country.csv"),
            Company2Country.objects.all(),
            "from_company",
            "to_country",
            [
                "relationship_type",
                "date_established_human",
                "date_finished_human",
                "date_confirmed_human",
                "proof_title",
                "proof",
            ]
        )
