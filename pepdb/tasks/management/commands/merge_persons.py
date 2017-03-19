# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import (
    Person, Person2Company, Person2Country, Person2Person, Declaration)
from tasks.models import PersonDeduplication
from django.db import transaction


FIELDS_TO_CONCATENATE = [
    "reputation_assets",
    "reputation_sanctions",
    "reputation_crimes",
    "reputation_manhunt",
    "reputation_convictions",
    "wiki"
]

FIELDS_TO_UPDATE = [
    "is_pep",
    "photo",
    "dob",
    "city_of_birth",
    "registration",
    "passport_id",
    "passport_reg",
    "tax_payer_id",
    "id_number",
]

class Command(BaseCommand):
    help = ('Takes finished tasks for persons deduplication and applies '
            'to the Person model')

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Apply deduplication results for real',
        )

    def handle(self, *args, **options):
        def _fetch_person(task, pk):
            try:
                return Person.objects.get(pk=pk)
            except person.DoesNotExist:
                self.stderr.write(
                    "\tperson with id {} doesn't exist, skipping".format(pk)
                )

            return None

        def _delete_person(task, pk):
            person = _fetch_person(task, pk)
            if person:
                self.stdout.write(
                    "\tdeleting person {} with id {}, imported={}".format(
                        person.full_name, person.pk, person.imported)
                )

                if options["real_run"]:
                    person.delete()

        for task in PersonDeduplication.objects.filter(
                applied=False).exclude(status="p"):

            self.stdout.write("Task #{}:".format(task.pk))

            if task.status == "a":
                self.stdout.write("\tskipping")

            if task.status in ["d1", "dd"]:
                _delete_person(task, task.person1_id)

            if task.status in ["d2", "dd"]:
                _delete_person(task, task.person2_id)

            if task.status == "m":
                person1 = _fetch_person(task, task.person1_id)
                person2 = _fetch_person(task, task.person2_id)
                if person1 is None or person2 is None:
                    continue

                # Round 1: fight:
                if len(person1.full_name) > len(person2.full_name):
                    master = person1
                    donor = person2
                    self.stdout.write("\tpreferring {} over {}".format(
                        person1.full_name, person2.full_name))
                else:
                    master = person2
                    donor = person1

                    self.stdout.write("\tpreferring {} over {}".format(
                        person2.full_name, person1.full_name))

                # Transfering data fields

                # Those to concatenate
                for field in FIELDS_TO_CONCATENATE:
                    donor_val = getattr(donor, field)
                    master_val = getattr(master, field)

                    if donor_val.strip():
                        setattr(master, field, master_val + donor_val)

                        self.stdout.write("\tconcatenating content of {}".format(
                            field))

                # Those to overwrite
                for field in FIELDS_TO_UPDATE:
                    donor_val = getattr(donor, field)
                    master_val = getattr(master, field)

                    if donor_val and not master_val:
                        setattr(master, field, donor_val)

                        self.stdout.write("\treplacing content of {}".format(
                            field))

                    # Corner case:
                    if field == "dob":
                        if donor_val and master_val and (donor.dob_details < master.dob_details):
                            master.dob = donor.dob
                            master.dob_details = donor.dob_details

                            self.stdout.write("\timproving content of {} (replacing {} with {})".format(
                                field, master.dob, donor.dob))

                # Another corner case:
                if donor.type_of_official < master.type_of_official:
                    self.stdout.write("\tUpgrading pep level to {}".format(
                        donor.type_of_official))
                    master.type_of_official = donor.type_of_official

                if options["real_run"]:
                    master.save()

                # Merging relations with companies
                for p2c in Person2Company.objects.filter(
                        from_person_id=donor.pk):

                    self.stdout.write("\tchanging link {}".format(p2c))

                    if options["real_run"]:
                        p2c.from_person = master
                        p2c.save()

                # Merging relations with countries
                for p2c in Person2Country.objects.filter(
                        from_person_id=donor.pk):

                    self.stdout.write("\tchanging link {}".format(p2c))

                    if options["real_run"]:
                        p2c.from_person = master
                        p2c.save()

                # Merging relations with other persons
                for p2p in Person2Person.objects.filter(
                        from_person_id=donor.pk):

                    if Person2Person.objects.filter(
                            from_person_id=master.pk,
                            to_person_id=p2p.to_person_id).count() == 0:
                        self.stdout.write("\tchanging link {}".format(p2p))

                        if options["real_run"]:
                            p2p.from_person_id = master.pk
                            p2p.save()
                    else:
                        self.stdout.write("\ignoring link {}".format(p2p))

                for p2p in Person2Person.objects.filter(
                        to_person_id=donor.pk):

                    if Person2Person.objects.filter(
                            to_person_id=master.pk,
                            from_person_id=p2p.from_person_id).count() == 0:
                        self.stdout.write("\tchanging link {}".format(p2p))

                        if options["real_run"]:
                            p2p.to_person_id = master.pk
                            p2p.save()
                    else:
                        self.stdout.write("\ignoring link {}".format(p2p))

                # Merging declarations
                for decl in Declaration.objects.filter(
                        person=donor.pk):

                    if Declaration.objects.filter(
                            person=master.pk,
                            declaration_id=decl.declaration_id).count() == 0:

                        self.stdout.write(
                            "\tswitching declaration {}".format(decl))

                        if options["real_run"]:
                            decl.person = master
                            decl.save()
                    else:
                        self.stdout.write(
                            "\t not switching declaration {}".format(decl))

                # TODO: Move also DeclarationExtra

                self.stdout.write(
                    "\tkeeping {} with id {}".format(
                        master.pk, master.full_name)
                )

                self.stdout.write(
                    "\tdeleting {} with id {}, imported={}".format(
                        donor.pk, donor.full_name, donor.imported)
                )

                if options["real_run"]:
                    # Kill the donor!
                    # Raw SQL because otherwise django will also kill the old
                    # connections of donor person, which are stuck for some reason.
                    Person.objects.raw(
                        "DELETE from core_person WHERE id=%s", [donor.pk]
                    )

            if options["real_run"]:
                task.applied = True
                task.save()
