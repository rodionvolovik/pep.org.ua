# coding: utf-8
from __future__ import unicode_literals

import json
from core.utils import parse_address
from core.universal_loggers import NoOpLogger
from core.importers import strategies as st
from core.models import Company


class CompanyImporter(object):
    def __init__(self, logger=NoOpLogger):
        """
        Accepts specially carved logger proxy to report problems
        to during the creation/update of the object.
        """

        self.logger = logger

    def get_or_create_from_edr_record(self, obj_dict):
        """
        Kind of get_or_create method, to create or update company model
        instance using data from EDR. DOESN'T SAVE THE MODIFIED OBJECT

        Returns Company instance and a created flag
        """
        created = False

        edrpou = obj_dict["edrpou"].rjust(8, "0")

        if not obj_dict["edrpou"]:
            self.logger.error(
                "Не можу імпортувати юр. особу без ЄДРПОУ <%s>" %
                json.dumps(obj_dict, ensure_ascii=False)
            )
            return None, created

        parsed = parse_address(obj_dict["location"])

        # Not using get_or_create to avoid situation
        # when created object is saved immediately
        try:
            # Sometime in companies table we have more than one company
            # with same edrpou, that usually happens when company got
            # reorganized or resurrected or something else strange had
            # happened

            # Here we'll try to update the most record of the company
            # in business first by narrowing down the search by using
            # status field
            company = Company.objects.get(
                edrpou=edrpou,
                status=1
            )
        except Company.DoesNotExist:
            try:
                company = Company.objects.get(edrpou=edrpou)
            except Company.DoesNotExist:
                company = Company(
                    edrpou=edrpou,
                    name_uk=obj_dict["name"].strip(),
                    short_name_uk=obj_dict["short_name"].strip()
                )
                created = True
            except Company.MultipleObjectsReturned:
                self.logger.error(
                    "Не можу імпортувати юр. особу <%s>: в базі таких більше одної" %
                    json.dumps(obj_dict, ensure_ascii=False)
                )
                return None, created

        except Company.MultipleObjectsReturned:
            self.logger.error(
                "Не можу імпортувати юр. особу <%s>: в базі більше одної в статусі 'зареєстровано'" %
                json.dumps(obj_dict, ensure_ascii=False)
            )
            return None, created

        if parsed:
            zip_code, city_uk, street_uk, appt_uk = parsed
            update_dict = {
                "zip_code": zip_code,
                "city_uk": city_uk,
                "street_uk": street_uk,
                "appt_uk": appt_uk
            }
        else:
            update_dict = {
                "raw_address": obj_dict["location"]
            }

        for k, v in company._status_choices.items():
            if obj_dict["status"].lower() == v:
                update_dict["status"] = k
                break

        merger = st.Merger((
            ("^status$", st.replace_strategy),
            (".*", st.replace_if_empty_strategy),
        ))

        res = merger.merge(company, update_dict)

        for k, v in res.items():
            if v == st.MergeResult.OLD_VALUE:
                self.logger.warning(
                    "Не замінюю поле %s на %s для компанії %s, %s" % (
                        k,
                        update_dict[k],
                        company.name,
                        company.id
                    )
                )

        return company, created
