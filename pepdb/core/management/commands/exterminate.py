# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.translation import activate
from django.conf import settings

from core.models import Person, Person2Company, Person2Person
from tasks.models import TerminationNotice
from core.utils import ceil_date, render_date

class Command(BaseCommand):
    help = ('Layered checks to find all PEPs who is not PEP anymore')

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)

        # First pass: find those PEPs who resigned or has no position in public bodies/SE
        peps_by_position = Person.objects.filter(type_of_official=1, reason_of_termination__isnull=True).nocache()

        probably_not_peps = {}
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
                    action="review",

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

            # Not creating termination notice yet as we need to check also if resigned PEP
            # has no relatives who are still PEPs
            probably_not_peps[pep.pk] = pep, last_date_on_job

        # Second pass
        for pep, last_date_on_job in probably_not_peps.values():
            last_workplace = pep.last_workplace
            pep_position = "{} @ {}".format(last_workplace["company"], last_workplace["position"]) if last_workplace else ""

            # Let's check if our candidates has a friends in high places
            to_persons = list(Person2Person.objects.prefetch_related("to_person") \
                .filter(
                    from_person=pep,
                    # Національний публічний діяч, Іноземний публічний діяч, Діяч, що виконуює значні функції в міжнародній організації
                    to_person__type_of_official__in = [1, 2, 3],
                ).values_list("to_person", flat=True)
            )

            from_persons = list(Person2Person.objects.prefetch_related("from_persons") \
                .filter(
                    to_person=pep,
                    # Національний публічний діяч, Іноземний публічний діяч, Діяч, що виконуює значні функції в міжнародній організації
                    from_person__type_of_official__in = [1, 2, 3],
                ).values_list("from_person", flat=True)
            )

            # Here we have three possible options.
            # 1. PEP by position has no positions to make him PEP anymore and no connections to other PEPs
            # We need to change his profile and record the fact that he won't be a PEP after 3 years since resignation
            # 2. Same as #1 but has other PEPs by position in connections, which makes him a related person instead of PEP
            # We need to change his profile and make him a related person instead, after 3 years since his resignation
            # 3. He is connected to some ex-PEPs by position, who is also resigned.
            # Then we need to make him a related person and then remove him from PEPs after 3 years since last resignation
            # (his or his croonies) has passed

            just_let_him_die = False
            switch_him_to_related = False
            still_a_friend_of = None
            remove_him_from_related = False
            remove_him_from_related_since = {
                "dt": last_date_on_job.date_finished,
                "dt_details": last_date_on_job.date_finished_details,
                "dt_ceiled": ceil_date(last_date_on_job.date_finished, last_date_on_job.date_finished_details)
            }

            # TODO: ignore those who is resigned recently
            self.stdout.write("Reviewing {} who got {} friends in high places".format(
                pep, len(set(to_persons + from_persons))))

            if to_persons + from_persons:
                for friend in Person.objects.filter(pk__in=to_persons + from_persons):
                    # Check if we've found a PEP's friend who is not resigned yet:
                    if friend.pk not in probably_not_peps and not friend.reason_of_termination:
                        self.stdout.write(
                            "\tWe've found a friend {} who still holds office".format(friend)
                        )
                        switch_him_to_related = True
                        still_a_friend_of = friend
                        remove_him_from_related = False
                        # Let's get outta here
                        break

                    # When his friend resigned earlier too:
                    if friend.reason_of_termination:
                        self.stdout.write(
                            "\tWe've found a friend {} who is already resigned".format(friend)
                        )
                        friend_dt_ceiled = ceil_date(friend.termination_date, friend.termination_date_details)
                        if friend_dt_ceiled > remove_him_from_related_since["dt_ceiled"]:
                            still_a_friend_of = friend
                            remove_him_from_related = True
                            remove_him_from_related_since["dt_ceiled"] = friend_dt_ceiled
                            remove_him_from_related_since["dt"] = friend.termination_date
                            remove_him_from_related_since["dt_details"] = friend.termination_date_details

                    if friend.pk in probably_not_peps:
                        self.stdout.write(
                            "\tWe've found a friend {} who is also about to set to resigned".format(friend)
                        )

                        _, friend_last_date_on_job = probably_not_peps[friend.pk]
                        friend_dt_ceiled = ceil_date(
                            friend_last_date_on_job.date_finished,
                            friend_last_date_on_job.date_finished_details
                        )

                        if friend_dt_ceiled > remove_him_from_related_since["dt_ceiled"]:
                            still_a_friend_of = friend
                            remove_him_from_related = True
                            remove_him_from_related_since["dt_ceiled"] = friend_dt_ceiled
                            remove_him_from_related_since["dt"] = friend_last_date_on_job.date_finished
                            remove_him_from_related_since["dt_details"] = friend_last_date_on_job.date_finished_details
            else:
                just_let_him_die = True

            if not switch_him_to_related and not remove_him_from_related:
                # Even if person had friends in high places but they all lost
                # their position before he resigned, we'll just mark him as one
                # to fire
                just_let_him_die = True

            if just_let_him_die:
                # Person is not a PEP by position anymore and doesn't have other PEPs connected with him
                TerminationNotice.objects.get_or_create(
                    pep_name=pep.full_name,
                    person=pep,
                    new_person_status=2,  # Resigned
                    action="fire",

                    defaults={
                        "termination_date": last_date_on_job.date_finished,
                        "termination_date_details": last_date_on_job.date_finished_details,
                        "termination_date_ceiled": ceil_date(last_date_on_job.date_finished, last_date_on_job.date_finished_details),
                        "pep_position": pep_position,
                        "comments": '{} звільнився з посади "{}" у "{}"'.format(
                            last_date_on_job.date_finished_human,
                            last_date_on_job.relationship_type_uk,
                            last_date_on_job.to_company.name
                        ),
                    }
                )
            elif switch_him_to_related:
                # Person is not a PEP by position anymore but have related persons who are PEPs by position
                TerminationNotice.objects.get_or_create(
                    pep_name=pep.full_name,
                    person=pep,
                    action="change_type",

                    defaults={
                        "termination_date": last_date_on_job.date_finished,
                        "termination_date_details": last_date_on_job.date_finished_details,
                        "termination_date_ceiled": ceil_date(last_date_on_job.date_finished, last_date_on_job.date_finished_details),
                        "pep_position": pep_position,
                        "comments": '{} звільнився з посади "{}" у "{}" але залишився пов\'язаною особою до {}'.format(
                            last_date_on_job.date_finished_human,
                            last_date_on_job.relationship_type_uk,
                            last_date_on_job.to_company.name,
                            still_a_friend_of
                        ),
                    }
                )
            elif remove_him_from_related:
                # Person is not a PEP by position anymore and all his related persons who was PEPs by position
                # is also not a PEPs anymore
                TerminationNotice.objects.get_or_create(
                    pep_name=pep.full_name,
                    person=pep,
                    action="change_and_fire",
                    new_person_status=4,  # "Пов'язана особа або член сім'ї - ПЕП припинив бути ПЕПом"

                    defaults={
                        "termination_date": remove_him_from_related_since["dt"],
                        "termination_date_details": remove_him_from_related_since["dt_details"],
                        "termination_date_ceiled": remove_him_from_related_since["dt_ceiled"],
                        "pep_position": pep_position,
                        "comments": '{} звільнився з посади "{}" у "{}" але залишився пов\'язаною особою до {}, що теж звільнився {}'.format(
                            last_date_on_job.date_finished_human,
                            last_date_on_job.relationship_type_uk,
                            last_date_on_job.to_company.name,
                            still_a_friend_of,
                            render_date(remove_him_from_related_since["dt"],
                                        remove_him_from_related_since["dt_details"])
                        ),
                    }
                )
            else:
                self.stderr.write("Unknown action for {}".format(pep))