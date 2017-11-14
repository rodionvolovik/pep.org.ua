# coding: utf-8
from __future__ import unicode_literals
import logging
from collections import defaultdict

from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_noop as _
from django.utils.translation import ugettext_lazy

from jsonfield import JSONField

from core.fields import RedactorField
from core.utils import (
    parse_fullname, parse_family_member, RELATIONS_MAPPING, render_date)

from core.model.connections import Person2Person
from core.model.exc import CannotResolveRelativeException

logger = logging.getLogger(__name__)


class Declaration(models.Model):
    STATUS_CHOICES = (
        ('p', 'Не перевірено'),
        ('r', 'Не підходить'),
        ('a', 'Опубліковано'),
        ('c', 'Перевірити'),
    )

    declaration_id = models.CharField(
        "Ідентифікатор", max_length=50, db_index=True)

    last_name = models.CharField("Прізвище", max_length=40, blank=True)
    first_name = models.CharField("Ім'я", max_length=40, blank=True)
    patronymic = models.CharField("По-батькові", max_length=40, blank=True)
    position = models.CharField("Посада", max_length=512, blank=True)
    office = models.CharField("Відомство", max_length=512, blank=True)
    region = models.CharField("Регіон", max_length=50, blank=True)
    year = models.CharField("Рік", max_length=4, blank=True, db_index=True)
    source = JSONField(blank=True)
    url = models.URLField("Посилання", max_length=512, blank=True)
    confirmed = models.CharField(
        "Підтверджено", max_length=1, choices=STATUS_CHOICES, default="p",
        db_index=True)
    fuzziness = models.IntegerField("Відстань", default=0)
    person = models.ForeignKey("Person", default=None)
    nacp_declaration = models.BooleanField(
        "Декларація НАЗК", default=False, db_index=True)

    relatives_populated = models.BooleanField(
        "Родини немає, або вже внесена до БД", default=False, db_index=True)

    batch_number = models.IntegerField("Номер теки", default=0, db_index=True)

    def to_dict(self):
        d = model_to_dict(self, fields=[
            "year", "position_uk", "office_uk", "region_uk",
            "position_en", "office_en", "region_en", "url"
        ])

        d["income"] = self.source["income"]['5'].get("value")
        d["family_income"] = self.source["income"]['5'].get("family")

        return d

    @property
    def family(self):
        if not self.source:
            return []

        res = []
        if ("family" in self.source["general"] and
                self.source["general"]["family"]):

            res = [
                {
                    "relation":
                        member.get(
                            "relations",
                            member.get("relations_other", "")),

                    "name": member.get("family_name", "")
                } for member in self.source["general"]["family"]
                if (
                    member.get("family_name", "") and
                    (member["relations"] + member.get("relations_other", ""))
                )
            ]
        elif ("family_raw" in self.source["general"] and
                self.source["general"]["family_raw"]):
            res = map(
                parse_family_member,
                filter(None, self.source["general"]["family_raw"].split(";")))

        res = filter(None, res)

        for i, r in enumerate(res):
            res[i]["mapped"] = RELATIONS_MAPPING.get(
                r["relation"].lower(), "особи, які спільно проживають")

            (res[i]["last_name"], res[i]["first_name"], res[i]["patronymic"],
                res[i]["dob"]) = parse_fullname(r["name"])

        return res

    def __unicode__(self):
        return "%s %s" % (self.person, self.declaration_id)

    def get_income(self):
        resp = {
            "year": self.year,
            "position": self.position,
            "office": self.office,
            "url": self.url,
            "income_of_declarant": ugettext_lazy("Не зазначено"),
            "income_of_family": ugettext_lazy("Не зазначено"),
            "expenses_of_declarant": ugettext_lazy("Не зазначено"),
        }

        if self.nacp_declaration:
            resp["income_of_declarant"] = 0
            resp["income_of_family"] = 0
            resp["expenses_of_declarant"] = 0
            if isinstance(self.source["nacp_orig"].get("step_11"), dict):
                for income in self.source["nacp_orig"]["step_11"].values():
                    try:
                        person = income.get("person", "1")
                        income_size = float(income.get("sizeIncome", "0"))

                        if person == "1":
                            resp["income_of_declarant"] += income_size
                        else:
                            resp["income_of_family"] += income_size
                    except ValueError:
                        pass

            if isinstance(self.source["nacp_orig"].get("step_14"), dict):
                for expense in self.source["nacp_orig"]["step_14"].values():
                    try:
                        expense_amount = float(expense.get("costAmount", "0"))
                        resp["expenses_of_declarant"] += expense_amount
                    except (ValueError, AttributeError):
                        pass
        else:
            resp["expenses_of_declarant"] = ugettext_lazy("Не зазначалось")

            if "income" in self.source:
                resp["income_of_declarant"] = self.source["income"]['5'].get(
                    "value", ugettext_lazy("Не зазначено"))
                resp["income_of_family"] = self.source["income"]['5'].get(
                    "family", ugettext_lazy("Не зазначено"))

        return resp

    def get_assets(self):
        resp = {
            "year": self.year,
            "url": self.url,
            "nacp_declaration": self.nacp_declaration,
            "cash": {
                "declarant": {
                    "USD": 0.,
                    "UAH": 0.,
                    "EUR": 0.,
                    "OTH": [],
                },
                "family": {
                    "USD": 0.,
                    "UAH": 0.,
                    "EUR": 0.,
                    "OTH": [],
                }
            },
            "accounts": {
                "declarant": {
                    "USD": 0.,
                    "UAH": 0.,
                    "EUR": 0.,
                    "OTH": [],
                    "banks": set(),
                },
                "family": {
                    "USD": 0.,
                    "UAH": 0.,
                    "EUR": 0.,
                    "OTH": [],
                    "banks": set(),
                }
            },
            "misc": {
                "declarant": {
                    "USD": 0.,
                    "UAH": 0.,
                    "EUR": 0.,
                    "OTH": [],
                },
                "family": {
                    "USD": 0.,
                    "UAH": 0.,
                    "EUR": 0.,
                    "OTH": [],
                }
            }
        }

        if self.nacp_declaration:
            data = self.source["nacp_orig"]

            if isinstance(data.get("step_12"), dict):
                for cash_rec in data["step_12"].values():
                    if isinstance(cash_rec, dict):
                        k = "misc"
                        rec_type = cash_rec.get("objectType", "").lower()
                        owner = "declarant" if cash_rec.get("person", "1") == "1" else "family"
                        amount = float(cash_rec.get("sizeAssets", "0") or "0")

                        currency = cash_rec.get("assetsCurrency", "UAH").upper()

                        if rec_type == "кошти, розміщені на банківських рахунках":
                            bank_name = cash_rec.get("organization_ua_company_name") or \
                                cash_rec.get("organization_ukr_company_name", "")

                            bank_name = bank_name.strip()
                            k = "accounts"
                            resp[k][owner]["banks"].add(bank_name)
                        elif rec_type == "готівкові кошти":
                            k = "cash"

                        if currency in ("UAH", "USD", "EUR"):
                            resp[k][owner][currency] += amount
                        else:
                            resp[k][owner]["OTH"].append(
                                {"amount": amount, "currency": currency}
                            )
        else:
            for d_key, k in (("45", "declarant"), ("51", "family")):
                for a in self.source.get("banks", {}).get(d_key, []):
                    try:
                        currency = a.get("sum_units", "UAH") or "UAH"
                        amount = a.get("sum", 0.)
                        if currency == "грн":
                            currency = "UAH"

                        if currency in ("UAH", "USD", "EUR"):
                            resp["accounts"][k][currency] += float(amount)
                        else:
                            resp["accounts"][k]["OTH"].append(
                                {"amount": float(amount), "currency": currency}
                            )
                    except ValueError:
                        continue

        return resp

    def get_gifts(self):
        resp = {
            "year": self.year,
            "url": self.url,
            "gifts_of_declarant": ugettext_lazy("Не зазначено"),
            "gifts_of_family": ugettext_lazy("Не зазначено"),
        }

        if self.nacp_declaration:
            resp["gifts_of_declarant"] = 0
            resp["gifts_of_family"] = 0
            if isinstance(self.source["nacp_orig"].get("step_11"), dict):
                for income in self.source["nacp_orig"]["step_11"].values():
                    try:
                        rec_type = income.get("objectType", "").lower()
                        if rec_type not in [
                                "подарунок у негрошовій формі",
                                "подарунок у грошовій формі",
                                "благодійна допомога", "приз"]:
                            continue

                        person = income.get("person", "1")
                        income_size = float(income.get("sizeIncome", "0"))

                        if person == "1":
                            resp["gifts_of_declarant"] += income_size
                        else:
                            resp["gifts_of_family"] += income_size
                    except (ValueError, AttributeError):
                        pass
        else:
            if "income" in self.source:
                resp["gifts_of_declarant"] = self.source["income"]['11'].get(
                    "value", ugettext_lazy("Не зазначено"))

                resp["gifts_of_family"] = self.source["income"]['11'].get(
                    "family", ugettext_lazy("Не зазначено"))

        return resp

    def get_liabilities(self):
        resp = {
            "year": self.year,
            "url": self.url,
            "liabilities_of_declarant": defaultdict(float),
            "liabilities_of_family": defaultdict(float),
        }

        if self.nacp_declaration:
            if isinstance(self.source["nacp_orig"].get("step_13"), dict):
                for liability in self.source["nacp_orig"]["step_13"].values():
                    try:
                        person = liability.get("person", "1")
                        liability_amount = float(liability.get("sizeObligation", "0") or 0)
                        currency = liability.get("currency", "UAH") or "UAH"

                        if person == "1":
                            resp["liabilities_of_declarant"][currency] += liability_amount
                        else:
                            resp["liabilities_of_family"][currency] += liability_amount
                    except (ValueError, AttributeError):
                        pass
        else:
            if "liabilities" in self.source:
                for field in ["54", "55", "56", "57", "58", "59"]:
                    if field in self.source["liabilities"]:
                        try:
                            resp["liabilities_of_declarant"]["UAH"] += float(
                                (self.source["liabilities"][field].get("sum", "0") or "0").replace(",", "."))
                        except (ValueError, UnicodeEncodeError):
                            pass

                for field in ["60", "61", "62", "63", "64"]:
                    if field in self.source["liabilities"]:
                        try:
                            resp["liabilities_of_family"]["UAH"] += float(
                                (self.source["liabilities"][field].get("sum", "0") or "0").replace(",", "."))
                        except (ValueError, UnicodeEncodeError):
                            pass

        return resp

    def resolve_person(self, family_id):
        """
        Finds the relative mentioned in the declaration in
        PEP db.
        Returns person id and a flag set to true, if it was fuzzy
        match
        """

        if str(family_id) == "1":
            return self.person, False

        def _is_fuzzy_match(declaration_rec, person_rec):
            if (declaration_rec["lastname"].strip().lower() !=
                    person_rec.last_name.strip().lower()):
                return True
            if (declaration_rec["firstname"].strip().lower() !=
                    person_rec.first_name.strip().lower()):
                return True
            if (declaration_rec["middlename"].strip().lower() !=
                    person_rec.patronymic.strip().lower()):
                return True

            return False

        data = self.source["nacp_orig"]
        family = data.get("step_2")

        if isinstance(family, dict):
            if not family_id or family_id not in family:
                raise CannotResolveRelativeException(
                    "Cannot find person %s in the declaration %s" % (
                        family_id, self.declaration_id)
                )

            member = family[family_id]
        else:
            raise CannotResolveRelativeException(
                "Cannot find family section in the declaration %s" % (
                    self.declaration_id)
            )

        chunk1 = list(Person2Person.objects.filter(
            from_person_id=self.person_id,
            to_person__last_name_uk__iexact=member["lastname"].strip(),
            to_person__first_name_uk__iexact=member["firstname"].strip(),
            to_person__patronymic_uk__iexact=member["middlename"].strip()
        ).select_related("to_person")) + list(Person2Person.objects.filter(
            from_person_id=self.person_id,
            to_person__last_name_uk__trigram_similar=member["lastname"].strip(),
            to_person__first_name_uk__trigram_similar=member["firstname"].strip(),
            to_person__patronymic_uk__trigram_similar=member["middlename"].strip()
        ).select_related("to_person"))

        chunk2 = list(Person2Person.objects.filter(
            to_person_id=self.person_id,
            from_person__last_name_uk__iexact=member["lastname"].strip(),
            from_person__first_name_uk__iexact=member["firstname"].strip(),
            from_person__patronymic_uk__iexact=member["middlename"].strip()
        ).select_related("from_person")) + list(Person2Person.objects.filter(
            to_person_id=self.person_id,
            from_person__last_name_uk__trigram_similar=member["lastname"].strip(),
            from_person__first_name_uk__trigram_similar=member["firstname"].strip(),
            from_person__patronymic_uk__trigram_similar=member["middlename"].strip()
        ).select_related("from_person"))

        if len(set(chunk1)) + len(set(chunk2)) > 1:
            raise CannotResolveRelativeException(
                "Uh, oh, more than one connection between %s and %s %s %s" %
                (self.person, member["lastname"], member["firstname"],
                 member["middlename"])
            )

        for conn in chunk1:
            fuzzy_match = _is_fuzzy_match(member, conn.to_person)
            if fuzzy_match:
                logger.warning(
                    "It was fuzzy match between %s %s %s and the declarant %s" % (
                        member["lastname"], member["firstname"],
                        member["middlename"], conn.to_person)
                )
            return conn.to_person, fuzzy_match

        for conn in chunk2:
            fuzzy_match = _is_fuzzy_match(member, conn.from_person)
            if fuzzy_match:
                logger.warning(
                    "It was fuzzy match between %s %s %s and the declarant %s" % (
                        member["lastname"], member["firstname"],
                        member["middlename"], conn.from_person)
                )

            return conn.from_person, fuzzy_match

        raise CannotResolveRelativeException(
            "Cannot find person %s %s %s for the declarant %s" % (
                member["lastname"], member["firstname"], member["middlename"],
                self.person
            )
        )

    class Meta:
        verbose_name = "Декларація"
        verbose_name_plural = "Декларації"
        indexes = [
            models.Index(fields=['confirmed', 'fuzziness', 'batch_number']),
        ]


class DeclarationExtra(models.Model):
    person = models.ForeignKey("Person", related_name="declaration_extras")

    date_confirmed = models.DateField(
        "Дата", blank=True, null=True, db_index=True)

    date_confirmed_details = models.IntegerField(
        "точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    @property
    def date_confirmed_human(self):
        return render_date(self.date_confirmed,
                           self.date_confirmed_details)

    section = models.IntegerField(
        "Розділ декларації",
        choices=(
            (0, _("Загальна сума сукупного доходу, гривні")),
            (1, _("Дарунки, призи, виграші")),
            (2, _("Земельні ділянки")),
            (3, _("Житлові будинки")),
            (4, _("Квартири")),
            (5, _("Інше нерухоме майно")),
            (6, _("Транспортні засоби")),
            (7, _("Вклади у банках")),
            (8, _("Фінансові зобов’язання")),
            (9, _("Інші активи")),
        ),
        default=0,
        db_index=True
    )

    note = RedactorField("Текст")
    address = RedactorField("Адреса", blank=True)
    country = models.ForeignKey("Country", blank=True)

    class Meta:
        verbose_name = "Додаткова інформація про статки"
        verbose_name_plural = "Додаткова інформація про статки"
