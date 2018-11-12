# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from dateutil.parser import parse as dt_parse

from core.models import Person, Company, Person2Company
from tasks.models import AdHocMatch


class Command(BaseCommand):
    help = """
    Populate pep's DOB from manhunt records
    """

    def handle(self, *args, **options):
        successful = 0
        failed = 0

        for rec in (
            AdHocMatch.objects.filter(status="a", dataset_id="wanted_ia")
            .prefetch_related("person")
            .nocache()
        ):

            dob = dt_parse(rec.matched_json["BIRTH_DATE"], yearfirst=True).date()
            if rec.person.dob is None or rec.person.dob_details > 0:
                rec.person.dob = dob
                rec.person.dob_details == 0
                rec.person.save()
                self.stdout.write(
                    "Updated DOB of the person {} in pep db to {}".format(
                        rec.person, dob
                    )
                )

                successful += 1
            else:
                if dob != rec.person.dob:
                    self.stderr.write(
                        "DOB of the person {} in pep db and wanted DB differs ({} vs {})".format(
                            rec.person, rec.person.dob, dob
                        )
                    )
                    failed += 1
                else:
                    self.stdout.write(
                        "Not updating DOB of the person {} in pep db and wanted DB ({} vs {})".format(
                            rec.person, rec.person.dob, dob
                        )
                    )

        self.stdout.write(
            "update failed: %s, update successful: %s" % (failed, successful)
        )
