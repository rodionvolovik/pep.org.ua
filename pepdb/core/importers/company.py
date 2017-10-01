# coding: utf-8
from __future__ import unicode_literals

import json
import re
from django.db.models import Q
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

        edrpou = unicode(obj_dict["edrpou"]).rjust(8, "0")

        if not obj_dict["edrpou"]:
            self.logger.error(
                "Не можу імпортувати юр. особу без ЄДРПОУ <%s>" %
                json.dumps(obj_dict, ensure_ascii=False, default=str)
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
                    json.dumps(obj_dict, ensure_ascii=False, default=str)
                )
                return None, created

        except Company.MultipleObjectsReturned:
            self.logger.error(
                "Не можу імпортувати юр. особу <%s>: в базі більше одної в статусі 'зареєстровано'" %
                json.dumps(obj_dict, ensure_ascii=False, default=str)
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

    def get_or_create_from_unified_foreign_registry(self, obj_dict):
        """
        Kind of get_or_create method, to create or update company model
        instance using data from spreadsheet rows of unified format below:
        owner_name, company_name_declaration, company_name_en, zip, city, street,
        appt, country, company_code, status, notes, company_name_orig, link,
        founder_1,... founder_N

        Lookup for get is made using company_code (if present).
        If company_code is absent or no match is found, lookup is made by name
        DOESN'T SAVE THE MODIFIED OBJECT

        Returns Company instance and a created flag
        """
        created = False

        company_code = obj_dict["company_code"].strip().replace(" ", "")
        company_name_declaration = obj_dict["company_name_declaration"].strip()
        company_name_en = obj_dict["company_name_en"].strip()
        company_name_orig = obj_dict["company_name_orig"].strip()

        if obj_dict["country"].strip().lower() == "кіпр":
            company_code = re.sub("^HE\s?", "HE", company_code)
            company_code = re.sub("^ΗΕ\s?", "HE", company_code)
            company_code = re.sub("^H\.E\.\s?", "HE", company_code)
            company_code = re.sub("^Η\.E\.\s?", "HE", company_code)

        update_dict = {
            "zip_code": obj_dict["zip"].strip(),
            "city_uk": obj_dict["city"].strip(),
            "street_uk": obj_dict["street"].strip(),
            "appt_uk": obj_dict["appt"].strip(),
            "city_en": obj_dict["city"].strip(),
            "street_en": obj_dict["street"].strip(),
            "appt_en": obj_dict["appt"].strip(),
        }

        if any(v for k, v in obj_dict.items() if k.startswith("founder_")):
            update_dict["other_founders_uk"] = "\n".join(
                obj_dict[k] for k in sorted(obj_dict.keys()) if k.startswith("founder_")
            )

        if obj_dict["notes"].strip():
            update_dict["wiki_uk"] = '<p>%s</p>' % obj_dict["notes"].strip()

        if obj_dict["link"].strip():
            update_dict["wiki_uk"] = (
                update_dict.get("wiki_uk", "") +
                '<p><a href="%s" target="_blank">Запис в реєстрі</p>' % obj_dict["link"].strip()
            )
            update_dict["wiki_en"] = (
                update_dict.get("wiki_en", "") +
                '<p><a href="%s" target="_blank">Registry record</p>' % obj_dict["link"].strip()
            )

        if company_name_orig:
            update_dict["also_known_as"] = company_name_orig

        if company_name_declaration:
            update_dict["name_uk"] = company_name_declaration

        if company_name_en:
            update_dict["name_en"] = company_name_en

        if obj_dict["status"]:
            for k, v in Company._status_choices.items():
                if obj_dict["status"].lower() == v:
                    update_dict["status"] = k
                    break
            else:
                self.logger.warning(
                    "Ігноруємо незрозумілий статус для компанії <%s>" %
                    json.dumps(obj_dict, ensure_ascii=False)
                )

        if (not company_code and
                not company_name_declaration and
                not company_name_en and
                not company_name_orig):
            self.logger.error(
                "Не можу імпортувати іноземну юр. особу без коду або назви <%s>" %
                json.dumps(obj_dict, ensure_ascii=False)
            )
            return None, created

        # Not using get_or_create to avoid situation
        # when created object is saved immediately
        try:
            # Search by code first
            company = Company.objects.deep_get([("edrpou__iexact", company_code)])
        except (Company.DoesNotExist, Company.MultipleObjectsReturned):
            try:
                # Then refine the search if needed
                company = Company.objects.deep_get([
                    ("name_uk__iexact", company_name_declaration),
                    ("name_uk__iexact", company_name_en),
                    ("name_uk__iexact", company_name_orig),
                    ("name_en__iexact", company_name_declaration),
                    ("name_en__iexact", company_name_en),
                    ("name_en__iexact", company_name_orig)
                ])

                if (company.edrpou and company_code and
                        company.edrpou.lower() != company_code.lower()):
                    # We found a company by name, but it's probably a wrong one
                    self.logger.warning(
                        ("Юр. особа що була знайдена для запису %s за іменем має відмінний " +
                         "код реєстрації: %s, створюємо нову компанію") %
                        (json.dumps(obj_dict, ensure_ascii=False), company.edrpou)
                    )
                    raise Company.DoesNotExist()

            except Company.DoesNotExist:
                company = Company(edrpou=company_code)
                created = True
            except Company.MultipleObjectsReturned:
                self.logger.error(
                    "Не можу імпортувати юр. особу <%s>: в базі таких більше одної" %
                    json.dumps(obj_dict, ensure_ascii=False)
                )
                return None, created

        merger = st.Merger((
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
