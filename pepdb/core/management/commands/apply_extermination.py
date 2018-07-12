# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings

from tasks.models import TerminationNotice


class Command(BaseCommand):
    help = ('Apply results of extermination after manual checks made by editors')

    def add_arguments(self, parser):
        parser.add_argument(
            '--real_run',
            action='store_true',
            dest='real_run',
            default=False,
            help='Exterminate for real',
        )

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        fired = 0
        type_changed = 0
        applied = 0

        for t in TerminationNotice.objects.filter(status="a", applied=False).nocache().iterator():
            self.stdout.write("Applying action {} to a person {} because of {}".format(
                t.get_action_display(), t.pep_name, t.comments
            ))

            if t.person:
                applied += 1

                if t.action in ["fire", "change_and_fire", "fire_related"]:
                    t.person.reason_of_termination = t.new_person_status
                    t.person.termination_date = t.termination_date
                    t.person.termination_date_details = t.termination_date_details
                    fired += 1

                if t.action in ["change_type", "change_and_fire"]:
                    t.person.is_pep = False
                    t.person.type_of_official = 4
                    type_changed += 1

                if options["real_run"]:
                    t.applied = True
                    t.person.save()
                    t.save()

        self.stdout.write("Total processed: {}, fired: {}, type of official changed {}".format(
            applied, fired, type_changed
        ))
