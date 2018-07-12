# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging
import argparse
from copy import copy
from hashlib import sha1

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone

import tqdm
from dateutil.parser import parse as dt_parse
from unicodecsv import DictReader

from core.elastic_models import Person as ElasticPerson
from tasks.models import AdHocMatch


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("importer")


class Command(BaseCommand):
    help = """Highly volatile and expiremental stuff: a script that reads
and matches arbitrary datasets with names with the list of persons in DB"""

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset_file', type=argparse.FileType('r'),
            help='Any dataset in the following formats: json, jsonlines, csv',
        )

        parser.add_argument(
            'dataset_identifier',
            help='Dataset name (will be displayed in admin)',
        )

        parser.add_argument(
            '--filetype',
            choices=("json", "jsonlines", "csv"),
            required=True,
            help='Format of the dataset',
        )

        parser.add_argument(
            '--name_field',
            nargs="+",
            help='fields from dataset to use for the search'
        )

        parser.add_argument(
            '--render_field',
            nargs="*",
            help='fields from dataset to use for the search'
        )

        parser.add_argument(
            '--dedup_field',
            nargs="*",
            help='fields from dataset to use to avoid duplicates after repeated runs'
        )

        parser.add_argument(
            '--last_updated_from_dataset',
            help='The date of the export of the dataset'
        )

    def iter_dataset(self, fp, filetype):
        if filetype == "json":
            for l in json.load(fp):
                yield l

        elif filetype == "jsonlines":
            for l in fp:
                yield json.loads(l)

        elif filetype == "csv":
            r = DictReader(fp)
            for l in r:
                yield l

    def get_name(self, doc, fields):
        return " ".join(filter(None, (doc.get(x, None) for x in fields)))

    def search_for_person(self, name):
        base_q = {
            "query": name,
            "operator": "and",
            "fuzziness": 0,
            "fields": ["full_name", "names", "full_name_en", "also_known_as_uk", "also_known_as_en"]
        }

        fuzziness = 0
        while fuzziness < 3:
            base_q["fuzziness"] = fuzziness

            s = ElasticPerson.search().query({
                "multi_match": base_q
            })

            if s.count():
                return s.execute(), fuzziness

            fuzziness += 1

        return [], 0

    def get_default_render_fields(self, doc, name_fields):
        return sorted(k for k in doc.keys() if k not in name_fields)

    def represent_entry_from_dataset(self, doc, options):
        render_fields = options.get("render_field")
        if render_fields is None:
            render_fields = self.get_default_render_fields(doc, options["name_field"])

        return (
            tuple((k, doc.get(k)) for k in options["name_field"]) +
            tuple((k, doc.get(k)) for k in render_fields)
        )

    def get_doc_hash(self, doc, options):
        dedup_fields = options.get("dedup_field")

        if dedup_fields is None:
            if options.get("render_field") is None:
                dedup_fields = self.get_default_render_fields(doc, options["name_field"])
            else:
                dedup_fields = copy(options["render_field"])

            dedup_fields += options["name_field"]

        return sha1(json.dumps(
            {k: doc.get(k) for k in sorted(dedup_fields)}
        )).hexdigest()

    def handle(self, *args, **options):
        if "last_updated_from_dataset" in options:
            last_updated = dt_parse(options["last_updated_from_dataset"], dayfirst=True)
        else:
            last_updated = timezone.now()

        with tqdm.tqdm() as pbar:
            for i, item in enumerate(self.iter_dataset(options["dataset_file"], options["filetype"])):
                pbar.update(1)
                doc_hash = self.get_doc_hash(item, options)
                name = self.get_name(item, options["name_field"])

                if name:
                    rpr = dict(self.represent_entry_from_dataset(item, options))
                    found_persons, fuzziness = self.search_for_person(name)
                    for res in found_persons:
                        try:
                            obj, created = AdHocMatch.objects.get_or_create(
                                matched_json_hash=doc_hash,
                                dataset_id=options["dataset_identifier"],
                                person_id=res.id,
                                defaults={
                                    "pep_name": res.full_name,
                                    "pep_position": "{} @ {}".format(
                                        getattr(res, "last_job_title", ""),
                                        getattr(res, "last_workplace", "")
                                    ),
                                    "matched_json": rpr,
                                    "name_match_score": fuzziness,
                                    "last_updated_from_dataset": last_updated,
                                    "first_updated_from_dataset": last_updated
                                }
                            )

                            if not created:
                                obj.last_updated_from_dataset = last_updated
                                obj.save()

                        except IntegrityError:
                            logger.warning("Cannot find person {} with key {} in db".format(res.full_name, res.id))
