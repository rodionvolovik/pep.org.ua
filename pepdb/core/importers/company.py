# coding: utf-8
from __future__ import unicode_literals

import json
from core.utils import parse_address
from core.universal_loggers import NoOpLogger
from core.importers import strategies as st
from core.models import Company


class CompanyImporter(object):
    def __init__(self, logger=NoOpLogger):
        self.logger = logger

    def get_or_create_from_edr_record(self, obj_dict, logger=NoOpLogger()):
        """
        Kind of get_or_create method, to create or update company model
        instance using data from EDR.

        Returns Company instance and a created flag
        Accepts specially carved logger proxy to report problems
        to during the creation/update of the object.
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

        try:
            company, created = Company.objects.get_or_create(
                edrpou=edrpou,
                defaults={
                    "name_uk": obj_dict["name"].strip(),
                    "short_name_uk": obj_dict["short_name"].strip()
                }
            )
        except Company.MultipleObjectsReturned:
            self.logger.error(
                "Не можу імпортувати юр. особу <%s>: в базі таких більше одної" %
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
