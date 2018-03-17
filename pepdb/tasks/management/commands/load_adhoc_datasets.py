# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint
import json
import logging
import argparse
from hashlib import sha1
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

import tqdm
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

    def iter_dataset(self, fp, filetype):
        if filetype == "json":
            for l in json.load(fp):
                yield l

        elif filetype == "jsonlines":
            for l in fp.read():
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

    def represent_entry_from_dataset(self, doc, name_fields, render_fields):
        if render_fields is None:
            render_fields = sorted(k for k in doc.keys() if k not in name_fields)

        return (
            tuple((k, doc.get(k)) for k in name_fields) +
            tuple((k, doc.get(k)) for k in render_fields)
        )


    def handle(self, *args, **options):
        with tqdm.tqdm() as pbar:
            for i, item in enumerate(self.iter_dataset(options["dataset_file"], options["filetype"])):
                pbar.update(1)
                doc_hash = sha1(json.dumps(item, sort_keys=True)).hexdigest()
                name = self.get_name(item, options["name_field"])

                if name:
                    rpr = self.represent_entry_from_dataset(item, options["name_field"], options["render_field"])
                    found_persons, fuzziness = self.search_for_person(name)
                    for res in found_persons:
                        try:
                            AdHocMatch.objects.get_or_create(
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
                                }
                            )
                        except IntegrityError:
                            logger.warning("Cannot find person {} with key {} in db".format(res.full_name, res.id))
