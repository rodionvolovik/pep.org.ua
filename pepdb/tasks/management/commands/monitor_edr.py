# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models.functions import Lower
from django.utils.translation import activate
from django.conf import settings

from elasticsearch_dsl import Q
from fuzzywuzzy import fuzz

from core.models import Person2Company
from core.utils import ceil_date, floor_date
from tasks.elastic_models import EDRPOU
from tasks.models import EDRMonitoring


class Command(BaseCommand):
    help = "Check if the head of the company in DB matches those in the EDR"
    positions_to_monitor = (
        "керівник",
        "начальник",
        "голова районної державної адміністрації",
        "директор",
        "в.о. прокурора міста києва",
        "в.о. генерального директора",
        "в.о. генерального секретаря",
        "в.о. голови",
        "в.о. голови нбу",
        "в.о. голови правління",
        "в.о. голови рда",
        "в.о. директора",
        "в.о. керівника",
        "в.о. начальника",
        "в.о. начальника, голова комісії з ліквідаці",
        "в.о. прокурора області",
        "виконавчий директор",
        "військовий комісар",
        "генеральний директор",
        "генеральний прокурор україни",
        "голова",
        "голова комісії",
        "голова нбу",
        "голова ода",
        "голова правління",
        "голова президії партії",
        "голова ради партії",
        "голова рда",
        "голова ревізійонї комісії",
        "голова сбу",
        "голова служби зовнішньої розвідки україни",
        "голова суду",
        "голова фдму",
        "голова цвк",
        "керуючий санацією",
        "київський міський голова",
        "лідер партії",
        "президент",
        "прокурор ар крим",
        "прокурор міста києва",
        "прокурор області",
        "співголова",
        "т.в.о. генерального директора",
        "т.в.о. голови",
        "т.в.о. голови ода",
        "т.в.о. голови правління",
        "т.в.о. голови рда",
        "т.в.о. директора",
        "т.в.о. керівника",
        "т.в.о. начальника",
    )

    # TODO: time to move that somewhere
    status_order = (
        "зареєстровано",
        "зареєстровано, свідоцтво про державну реєстрацію недійсне",
        "порушено справу про банкрутство",
        "порушено справу про банкрутство (санація)",
        "в стані припинення",
        "припинено",
    )

    def search_for_company(self, edrpou):
        for order in self.status_order:
            res = EDRPOU.search().query(
                "bool", must=[Q("term", edrpou=edrpou), Q("term", status=order)]
            )
            ans = res.execute()
            if ans:
                break

        # Last attempt
        if not ans:
            res = EDRPOU.search().query("term", edrpou=edrpou)
            ans = res.execute()

        return ans

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)

        q = (
            Person2Company.objects.select_related("to_company", "from_person")
            .filter(to_company__state_company=True)
            .exclude(to_company__edrpou="")
            .annotate(rt_lower=Lower("relationship_type_uk"))
            .filter(rt_lower__in=self.positions_to_monitor)
        )

        for i, conn in enumerate(q):
            pep_name = (
                "{} {} {}".format(
                    conn.from_person.last_name,
                    conn.from_person.first_name,
                    conn.from_person.patronymic,
                )
                .replace("  ", " ")
                .lower()
            )

            pep_position = conn.relationship_type_uk.lower()
            company_edrpou = conn.to_company.edrpou.lstrip("0")
            if conn.to_company.closed_on and conn.to_company.status in [
                2
            ]:  # 2 is for prypyneno
                closed_on = ceil_date(
                    conn.to_company.closed_on, conn.to_company.closed_on_details
                )
            else:
                closed_on = None

            ans = self.search_for_company(company_edrpou)
            for company in ans:
                if company.head is None:
                    continue

                edr_name = company.head.lower()

                latest_rec = EDRMonitoring.objects.filter(
                    company_edrpou=company_edrpou
                ).order_by("-edr_date")

                if closed_on is not None and closed_on < company.last_update.date():
                    self.stderr.write(
                        "Company in {} were closed on {} before the date {} from registry, skipping it".format(
                            conn, closed_on, company.last_update.date()
                        )
                    )
                    continue

                if conn.date_established:
                    if (
                        floor_date(conn.date_established, conn.date_established_details)
                        >= company.last_update.date()
                    ):
                        self.stderr.write(
                            "Connection {} started on {} after the date {} from registry, skipping it".format(
                                conn,
                                floor_date(
                                    conn.date_established, conn.date_established_details
                                ),
                                company.last_update.date(),
                            )
                        )
                        continue

                if conn.date_finished:
                    if (
                        ceil_date(conn.date_finished, conn.date_finished_details)
                        <= company.last_update.date()
                    ):
                        self.stderr.write(
                            "Connection {} finished on {} before the date {} from registry, skipping it".format(
                                conn,
                                ceil_date(
                                    conn.date_finished, conn.date_finished_details
                                ),
                                company.last_update.date(),
                            )
                        )
                        continue

                try:
                    rec = EDRMonitoring.objects.get(
                        pep_name=pep_name,
                        pep_position=pep_position,
                        edr_name=edr_name,
                        company_edrpou=company_edrpou,
                    )

                    if latest_rec:
                        if (
                            latest_rec[0].pk != rec.pk
                            and latest_rec[0].edr_date > rec.edr_date
                            and rec.status != "p"
                        ):
                            self.stderr.write(
                                "Watch out! Some zombies are there: {} @ {}, {} ({})".format(
                                    pep_name,
                                    pep_position,
                                    conn.to_company.name,
                                    company_edrpou,
                                )
                            )
                            rec.status = "r"
                    rec.save()

                    self.stdout.write(
                        "Record {}, {}, {}, {} already exists".format(
                            pep_name, pep_position, edr_name, company_edrpou
                        )
                    )
                except EDRMonitoring.DoesNotExist:
                    diff = fuzz.token_set_ratio(edr_name, pep_name, force_ascii=False)

                    if diff == 100:
                        continue

                    if diff > 90:
                        status = "i"
                    else:
                        status = "p"

                    rec = EDRMonitoring.objects.create(
                        pep_name=pep_name,
                        pep_position=pep_position,
                        edr_name=edr_name,
                        company_edrpou=company_edrpou,
                        pep_company_json=conn.to_company.to_dict(),
                        edr_company_json=company.to_dict(),
                        name_match_score=diff,
                        status=status,
                        company_id=conn.to_company_id,
                        relation_id=conn.pk,
                        person_id=conn.from_person_id,
                        edr_date=company.last_update,
                    )
