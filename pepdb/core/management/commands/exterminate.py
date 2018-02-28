# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings

from core.models import Person, Person2Company
from tasks.models import TerminationNotice


class Command(BaseCommand):
    help = ('Layered checks to find all PEPs who is not PEP anymore')

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)

        # First pass: find those PEPs who resigned or has no position in public bodies/SE
        peps_by_position = Person.objects.filter(type_of_official=1, reason_of_termination__isnull=True).nocache()

        for pep in peps_by_position:
            has_open_positions = Person2Company.objects \
                .prefetch_related("to_company") \
                .filter(
                    from_person=pep,
                    date_finished__isnull=True,
                    to_company__state_company=True
                ) \
                .exclude(
                    relationship_type_uk__in=["Клієнт банку"]
                ).exists()

            # Person got a connection to state company and not yet resigned
            # moving forwared
            if has_open_positions:
                continue

            last_workplace = pep.last_workplace
            pep_position = "{} @ {}".format(last_workplace["company"], last_workplace["position"]) if last_workplace else ""

            has_connections_to_state = Person2Company.objects \
                .prefetch_related("to_company") \
                .filter(
                    from_person=pep,
                    to_company__state_company=True
                ) \
                .exclude(
                    relationship_type_uk__in=["Клієнт банку"]
                ).exists()

            if not has_connections_to_state:
                # PEP by position has no connections to state at all
                TerminationNotice.objects.get_or_create(
                    pep_name=pep.full_name,
                    person=pep,

                    defaults={
                        "pep_position": pep_position,
                        "comments": "Взагалі нема зв'язків з юр. особами які роблять ПЕПом за посадою",
                    }
                )
                continue

            last_date_on_job = Person2Company.objects \
                .prefetch_related("to_company") \
                .filter(
                    from_person=pep,
                    to_company__state_company=True
                ) \
                .order_by("-date_finished") \
                .exclude(
                    relationship_type_uk__in=["Клієнт банку"]
                ).first()

            # PEP resigned from SE
            TerminationNotice.objects.get_or_create(
                    pep_name=pep.full_name,
                    person=pep,
                    new_person_status=2,  # Resigned
                    termination_date=last_date_on_job.date_finished,
                    termination_date_details=last_date_on_job.date_finished_details,

                    defaults={
                        "pep_position": pep_position,
                        "comments": '{} звільнився з посади "{}" у "{}"'.format(
                            last_date_on_job.date_finished_human,
                            last_date_on_job.relationship_type_uk,
                            last_date_on_job.to_company.name
                        ),
                    }
                )
