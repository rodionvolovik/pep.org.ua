# coding: utf-8
from __future__ import unicode_literals
from copy import copy
from collections import defaultdict

from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_noop as _
from django.utils.translation import ugettext_lazy, activate, deactivate
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist

from redactor.fields import RedactorField

from core.model.base import AbstractNode
from core.model.translations import Ua2EnDictionary
from core.utils import render_date, lookup_term


class CompanyManager(models.Manager):
    def deep_get(self, clauses):
        """
        Two-stage search which takes into account company status
        """

        query = Q()
        for field, value in clauses:

            if value:
                if len(value) < 2:
                    continue

                query |= Q(**{field: value})

        try:
            # Sometime in companies table we have more than one company
            # with same code, that usually happens when company got
            # reorganized or resurrected or something else strange had
            # happened

            # Here we'll try to update the most record of the company
            # in business first by narrowing down the search by using
            # status field
            return self.get(query & Q(status=1))
        except ObjectDoesNotExist:
            return self.get(query)


# to_*_dict methods are used to convert two main entities that we have, Person
# and Company into document indexable by ElasticSearch.
# Links between Persons, Person and Company, Companies, Person and Country,
# Company and Country is also converted to subdocuments and attached to
# Person/Company documents. Because Person and Company needs different
# subdocuments, Person2Company has two different methods, to_person_dict and
# to_company_dict. For the same reason Person2Person and Company2Company has
# to_dict/to_dict_reverse because same link provides info to both persons.


class Company(models.Model, AbstractNode):
    _status_choices = {
        0: _("інформація відсутня"),
        1: _("зареєстровано"),
        2: _("припинено"),
        3: _("в стані припинення"),
        4: _("зареєстровано, свідоцтво про державну реєстрацію недійсне"),
        5: _("порушено справу про банкрутство"),
        6: _("порушено справу про банкрутство (санація)"),
        7: _("розпорядження майном"),
        8: _("ліквідація"),
    }

    name = models.CharField("Повна назва", max_length=512)
    short_name = models.CharField("Скорочена назва", max_length=200,
                                  blank=True)

    also_known_as = models.TextField("Назви іншими мовами або варіації", blank=True)

    publish = models.BooleanField("Опублікувати", default=False)
    founded = models.DateField("Дата створення", blank=True, null=True)
    founded_details = models.IntegerField(
        "Дата створення: точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    status = models.IntegerField(
        "Поточний стан",
        choices=_status_choices.items(),
        default=0
    )
    closed_on = models.DateField("Дата припинення", blank=True, null=True)
    closed_on_details = models.IntegerField(
        "Дата припинення: точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    @property
    def founded_human(self):
        return render_date(self.founded,
                           self.founded_details)

    state_company = models.BooleanField(
        "Керівник — ПЕП", default=False)

    legal_entity = models.BooleanField(
        "Юрособа", default=True)

    edrpou = models.CharField(
        "ЄДРПОУ", max_length=50, blank=True)

    zip_code = models.CharField("Індекс", max_length=20, blank=True)
    city = models.CharField("Місто", max_length=255, blank=True)
    street = models.CharField("Вулиця", max_length=100, blank=True)
    appt = models.CharField("№ будинку, офісу", max_length=50, blank=True)
    raw_address = models.TextField('"Сира" адреса', blank=True)

    wiki = RedactorField("Вікі-стаття", blank=True)

    other_founders = RedactorField(
        "Інші засновники",
        help_text="Через кому, не PEP", blank=True)

    other_recipient = models.CharField(
        "Бенефіціарій", help_text="Якщо не є PEPом", blank=True,
        max_length=200)

    other_owners = RedactorField(
        "Інші власники",
        help_text="Через кому, не PEP", blank=True)

    other_managers = RedactorField(
        "Інші керуючі",
        help_text="Через кому, не PEP", blank=True)

    bank_name = RedactorField("Фінансова інформація", blank=True)

    sanctions = RedactorField("Санкції", blank=True)

    related_companies = models.ManyToManyField(
        "self", through="Company2Company", symmetrical=False)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "short_name__icontains", "name__icontains")

    def __unicode__(self):
        return self.short_name or self.name

    def to_dict(self):
        d = model_to_dict(self, fields=[
            "id", "name_uk", "short_name_uk", "name_en", "short_name_en",
            "state_company", "edrpou", "wiki", "city", "street",
            "other_founders", "other_recipient", "other_owners",
            "other_managers", "bank_name", "also_known_as"])

        d["related_persons"] = [
            i.to_person_dict()
            for i in self.from_persons.select_related("from_person")]

        d["related_countries"] = [
            i.to_dict()
            for i in self.from_countries.select_related("to_country")]

        d["related_companies"] = [
            i.to_dict()
            for i in self.to_companies.select_related("to_company")] + [
            i.to_dict_reverse()
            for i in self.from_companies.select_related("from_company")
        ]

        suggestions = []

        for field in (d["name_uk"], d["short_name_uk"],
                      d["name_en"], d["short_name_en"]):
            if not field:
                continue

            chunks = list(
                map(lambda x: x.strip("'\",.-“”«»"), field.split(" ")))

            for i in xrange(len(chunks)):
                variant = copy(chunks)
                variant = [variant[i]] + variant[:i] + variant[i + 1:]
                suggestions.append(" ".join(variant))

        if self.edrpou:
            suggestions.append(self.edrpou.lstrip("0"))

            if self.edrpou.isdigit():
                suggestions.append(self.edrpou.rjust(8, "0"))

        d["name_suggest"] = [
            {"input": x} for x in suggestions
        ]

        d["name_suggest_output"] = d["short_name_uk"] or d["name_uk"]
        d["name_suggest_output_en"] = d["short_name_en"] or d["name_en"]

        d["_id"] = d["id"]

        return d

    def save(self, *args, **kwargs):
        if not self.name_en:
            t = Ua2EnDictionary.objects.filter(
                term__iexact=lookup_term(self.name_uk)).first()

            if t and t.translation:
                self.name_en = t.translation

        if not self.short_name_en:
            t = Ua2EnDictionary.objects.filter(
                term__iexact=lookup_term(self.short_name_en)).first()

            if t and t.translation:
                self.short_name_en = t.translation

        super(Company, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("company_details", kwargs={"company_id": self.pk})

    def localized_url(self, locale):
        activate(locale)
        url = self.get_absolute_url()
        deactivate()
        return url

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    @property
    def all_related_persons(self):
        related_persons = [
            (i.relationship_type_uk, i.from_person, i)
            for i in self.from_persons.select_related("from_person").defer(
                "from_person__reputation_assets",
                "from_person__reputation_crimes",
                "from_person__reputation_manhunt",
                "from_person__reputation_convictions",
                "from_person__wiki",
                "from_person__names",
                "from_person__hash"
            ).order_by("from_person__last_name_uk", "from_person__first_name_uk")
        ]

        res = {
            "managers": [],
            "founders": [],
            "sanctions": [],
            "rest": []
        }

        for rtp, p, rel in related_persons:
            add_to_rest = True
            p.rtype = rtp
            p.connection = rel

            if rtp.lower() in [
                    "керівник", "перший заступник керівника",
                    "заступник керівника", "голова", "заступник голови",
                    "перший заступник голови", "член правління", "член ради",
                    "член", "директор", "підписант", "номінальний директор",
                    "керуючий"]:
                res["managers"].append(p)

                add_to_rest = False
            elif rtp.lower() in [
                    "засновники", "засновник/учасник",
                    "колишній засновник/учасник", "бенефіціарний власник",
                    "номінальний власник"]:
                res["founders"].append(p)
                add_to_rest = False

            if p.reputation_sanctions:
                res["sanctions"].append(p)
                add_to_rest = False

            if add_to_rest:
                res["rest"].append(p)

        return res

    @property
    def all_related_countries(self):
        related_countries = [
            (i.relationship_type, i.to_country, i)
            for i in self.from_countries.select_related("to_country")
        ]

        res = defaultdict(list)

        for rtp, p, rel in related_countries:
            p.rtype = rtp
            p.connection = rel

            if rtp == "registered_in":
                res[rtp].append(p)
            else:
                res["rest"].append(p)

        return res

    @property
    def all_related_companies(self):
        related_companies = [
            (i.relationship_type, i.to_company, i)
            for i in self.to_companies.select_related("to_company").defer(
                "to_company__wiki",
                "to_company__other_founders",
                "to_company__other_recipient",
                "to_company__other_owners",
                "to_company__other_managers",
                "to_company__bank_name",
                "to_company__sanctions",
            )
        ] + [
            (i.reverse_relationship_type, i.from_company, i)
            for i in self.from_companies.select_related("from_company").defer(
                "from_company__wiki",
                "from_company__other_founders",
                "from_company__other_recipient",
                "from_company__other_owners",
                "from_company__other_managers",
                "from_company__bank_name",
                "from_company__sanctions",
            )
        ]

        res = {
            "founders": [],
            "rest": [],
            "all": []
        }

        for rtp, p, rel in sorted(related_companies, key=lambda x: x[1].name_uk):
            p.rtype = rtp
            p.connection = rel

            if rtp in ["Засновник", "Співзасновник",
                       "Колишній власник/засновник",
                       "Колишній співвласник/співзасновник"]:
                res["founders"].append(p)
            else:
                res["rest"].append(p)

            res["all"].append(p)

        return res

    def get_node_info(self, with_connections=False):
        res = super(Company, self).get_node_info(with_connections)
        res["name"] = self.name
        res["description"] = self.edrpou
        res["kind"] = unicode(
            ugettext_lazy("Державна компанія чи установа")
            if self.state_company else
            ugettext_lazy("Приватна компанія")
        )

        if with_connections:
            connections = []

            persons = self.all_related_persons
            for k in persons.values():
                for p in k:
                    connections.append({
                        "relation": p.connection.relationship_type,
                        "node": p.get_node_info(False),
                        "model": p.connection._meta.model_name,
                        "pk": p.connection.pk
                    })

            # Because of a complicated logic here we are piggybacking on
            # existing method that handles both directions of relations
            for c in self.all_related_companies["all"]:
                connections.append({
                    "relation": unicode(ugettext_lazy(c.rtype)),
                    "node": c.get_node_info(False),
                    "model": c.connection._meta.model_name,
                    "pk": c.connection.pk
                })

            countries = self.from_countries.select_related("to_country")
            for c in countries:
                connections.append({
                    "relation": unicode(
                        ugettext_lazy(c.get_relationship_type_display())),
                    "node": c.to_country.get_node_info(False),
                    "model": c._meta.model_name,
                    "pk": c.pk
                })

            res["connections"] = connections

        return res

    @property
    def closed_on_human(self):
        return render_date(self.closed_on,
                           self.closed_on_details)

    objects = CompanyManager()

    class Meta:
        verbose_name = "Юридична особа"
        verbose_name_plural = "Юридичні особи"
