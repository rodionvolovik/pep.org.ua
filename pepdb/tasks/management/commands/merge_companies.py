# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import connection
from core.models import (
    Company, Person2Company, Company2Country, Company2Company)
from tasks.models import CompanyDeduplication


FIELDS_TO_CONCATENATE = [
    "also_known_as",
    "bank_name_en",
    "other_founders_en",
    "other_managers_en",
    "other_owners_en",
    "other_recipient_en",
    "sanctions_en",
    "wiki_en",
    "bank_name_uk",
    "other_founders_uk",
    "other_managers_uk",
    "other_owners_uk",
    "other_recipient_uk",
    "sanctions_uk",
    "wiki_uk",
]

FIELDS_TO_UPDATE = [
    "founded",
    "closed_on",
    "state_company",
    "legal_entity",

    "edrpou",
    "zip_code",

    "city_en",
    "street_en",
    "appt_en",
    "city_uk",
    "street_uk",
    "appt_uk",
    "raw_address",

    "short_name_en",
    "short_name_uk",
    "name_en",
]

class Command(BaseCommand):
    help = ('Takes finished tasks for companies deduplication and applies '
            'to the Company model')

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
        def _fetch_company(task, pk):
            try:
                return Company.objects.get(pk=pk)
            except Company.DoesNotExist:
                self.stderr.write(
                    "\tcompany with id {} doesn't exist, skipping".format(pk)
                )

            return None

        def _delete_company(task, pk):
            company = _fetch_company(task, pk)
            if company:
                self.stdout.write(
                    "\tdeleting company {} with id {}".format(
                        company.name_uk, company.pk)
                )

                if options["real_run"]:
                    company.delete()

        cursor = connection.cursor()
        for task in CompanyDeduplication.objects.filter(
                applied=False).exclude(status="p"):

            self.stdout.write("Task #{}:".format(task.pk))

            if task.status == "a":
                self.stdout.write("\tskipping")

            if task.status in ["d1", "dd"]:
                if task.status == "d1":
                    self.stdout.write(
                        "\tkeeping {}".format(
                            task.company2_id)
                    )

                _delete_company(task, task.company1_id)

            if task.status in ["d2", "dd"]:
                if task.status == "d2":
                    self.stdout.write(
                        "\tkeeping {}".format(
                            task.company1_id)
                    )

                _delete_company(task, task.company2_id)

            if task.status == "m":
                company1 = _fetch_company(task, task.company1_id)
                company2 = _fetch_company(task, task.company2_id)
                if company1 is None or company2 is None:
                    continue

                # Round 1: fight:
                if len(company1.name_uk) > len(company2.name_uk):
                    master = company1
                    donor = company2
                    self.stdout.write("\tpreferring {} over {}".format(
                        company1.name_uk, company2.name_uk))
                else:
                    master = company2
                    donor = company1

                    self.stdout.write("\tpreferring {} over {}".format(
                        company2.name_uk, company1.name_uk))

                # Transfering data fields

                # Those to concatenate
                for field in FIELDS_TO_CONCATENATE:
                    donor_val = getattr(donor, field)
                    master_val = getattr(master, field)

                    if donor_val and donor_val.strip():
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

                    # Corner cases on dates:
                    if field == "founded":
                        if donor_val and master_val and (donor.founded_details < master.founded_details):
                            master.founded = donor.founded
                            master.founded_details = donor.founded_details

                            self.stdout.write("\timproving content of {} (replacing {} with {})".format(
                                field, master.founded, donor.founded))

                    if field == "closed_on":
                        # TODO: check for statuses?
                        if donor_val and master_val and (donor.closed_on_details < master.closed_on_details):
                            master.closed_on = donor.closed_on
                            master.closed_on_details = donor.closed_on_details

                            self.stdout.write("\timproving content of {} (replacing {} with {})".format(
                                field, master.closed_on, donor.closed_on))

                # Another corner case:
                if donor.status < master.status:
                    self.stdout.write("\tUpgrading company level to {}".format(
                        donor.status))
                    master.status = donor.status

                if master.status < 3 and master.closed_on:
                    self.stderr.write("\tAlarm, company is not closed but has status {}".format(
                        master.status))

                if options["real_run"]:
                    master.save()

                # Merging relations with companies
                for p2c in Person2Company.objects.filter(
                        to_company_id=donor.pk):

                    self.stdout.write("\tchanging link {}".format(p2c))

                    if options["real_run"]:
                        p2c.to_company = master
                        p2c.save()

                # Merging relations with countries
                for c2c in Company2Country.objects.filter(
                        from_company_id=donor.pk):

                    self.stdout.write("\tchanging link {}".format(c2c))

                    if options["real_run"]:
                        c2c.from_company = master
                        c2c.save()

                # Merging relations with other companies
                for c2c in Company2Company.objects.filter(
                        from_company_id=donor.pk):

                    self.stdout.write("\tchanging link {}".format(c2c))

                    if options["real_run"]:
                        c2c.from_company_id = master.pk
                        c2c.save()

                for c2c in Company2Company.objects.filter(
                        to_company_id=donor.pk):

                    self.stdout.write("\tchanging link {}".format(c2c))

                    if options["real_run"]:
                        c2c.to_company_id = master.pk
                        c2c.save()

                self.stdout.write(
                    "\tkeeping {} with id {}".format(
                        master.pk, master.name_uk)
                )

                self.stdout.write(
                    "\tdeleting {} with id {}".format(
                        donor.pk, donor.name_uk)
                )

                if options["real_run"]:
                    # Kill the donor!
                    # Raw SQL because otherwise django will also kill the old
                    # connections of donor company, which are stuck for some reason.
                    cursor.execute("DELETE from core_company WHERE id=%s", [donor.pk])

            if options["real_run"]:
                task.applied = True
                task.save()
