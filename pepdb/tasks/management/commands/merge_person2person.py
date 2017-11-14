# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict


from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import Person2Person
from django.forms.models import model_to_dict
from django.db import transaction


FIELDS_TO_CONCATENATE = [
    "proof_title",
    "proof",
]

FIELDS_TO_UPDATE = [
    "declarations",
    "date_established",
    "date_finished",
    "date_confirmed",
    "from_relationship_type",
    "to_relationship_type",
]


class Command(BaseCommand):
    help = ('Makes attempts to deduplicate person2person connections')

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Deduplicate for real',
        )

    def handle(self, *args, **options):
        res = defaultdict(list)

        for p2p in Person2Person.objects.all():
            res[(p2p.from_person_id, p2p.to_person_id)].append(p2p)

        for r in res.values():
            if len(r) == 1:
                continue

            master = r[0]
            donor = r[1]

            self.stdout.write("Pair {} vs {}:".format(
                master, donor))

            if ((master.from_relationship_type != donor.from_relationship_type) and
                    donor.from_relationship_type and master.from_relationship_type):
                self.stdout.write("\tIgnoring because of discrepancy: {} vs {}".format(
                    master.from_relationship_type, donor.from_relationship_type)
                )
                continue

            if ((master.to_relationship_type != donor.to_relationship_type) and
                    master.to_relationship_type and donor.to_relationship_type):
                self.stdout.write("\tIgnoring because of discrepancy: {} vs {}".format(
                    master.to_relationship_type, donor.to_relationship_type)
                )
                continue

            for field in FIELDS_TO_CONCATENATE:
                donor_val = getattr(donor, field)
                master_val = getattr(master, field)

                if donor_val.strip():
                    master_val = master_val + ", " + donor_val
                    setattr(master, field, master_val)

                    self.stdout.write("\tconcatenating content of {}: {}".format(
                        field, master_val))

            # Corner case
            master.declarations = list(
                set(master.declarations or []) |
                set(donor.declarations or [])
            )

            for field in FIELDS_TO_UPDATE:
                donor_val = getattr(donor, field)
                master_val = getattr(master, field)

                if donor_val:
                    if not master_val:
                        setattr(master, field, donor_val)

                        self.stdout.write("\treplacing content of {}".format(
                            field))
                    else:
                        self.stdout.write(
                            "\tnot replacing content of {} ({} vs {})".format(
                                field, master_val, donor_val))

                if field == "declarations":
                    setattr(
                        master, field,
                        list(set(master_val or []) | set(donor_val or []))
                    )

                # Corner cases:
                if field.startswith("date_"):
                    subfield = field + "_details"
                    donor_val_details = getattr(donor, subfield)
                    master_val_details = getattr(master, subfield)

                    if donor_val and master_val and (
                            donor_val_details < master_val_details):

                        setattr(master, field, donor_val)
                        setattr(master, subfield, donor_val_details)

                        self.stdout.write(
                            "\timproving content of {} (replacing {} with {})".format(
                                field, master_val, donor_val))

            if options["real_run"]:
                master.save()
                donor.delete()
