# coding: utf-8
from __future__ import unicode_literals
import re
from copy import copy, deepcopy
from collections import defaultdict

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.utils.translation import ugettext_lazy, activate, get_language
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist

from core.fields import RedactorField

from core.model.base import AbstractNode
from core.model.translations import Ua2EnDictionary
from core.utils import render_date, lookup_term, translate_into


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

    name = models.CharField(_("Повна назва"), max_length=512)
    short_name = models.CharField(_("Скорочена назва"), max_length=200,
                                  blank=True)

    also_known_as = models.TextField(_("Назви іншими мовами або варіації"), blank=True)

    publish = models.BooleanField(_("Опублікувати"), default=False)
    founded = models.DateField(_("Дата створення"), blank=True, null=True)
    founded_details = models.IntegerField(
        _("Дата створення: точність"),
        choices=(
            (0, _("Точна дата")),
            (1, _("Рік та місяць")),
            (2, _("Тільки рік")),
        ),
        default=0)

    status = models.IntegerField(
        _("Поточний стан"),
        choices=_status_choices.items(),
        default=0
    )
    closed_on = models.DateField(_("Дата припинення"), blank=True, null=True)
    closed_on_details = models.IntegerField(
        _("Дата припинення: точність"),
        choices=(
            (0, _("Точна дата")),
            (1, _("Рік та місяць")),
            (2, _("Тільки рік")),
        ),
        default=0)

    @property
    def founded_human(self):
        return render_date(self.founded,
                           self.founded_details)

    state_company = models.BooleanField(
        _("Керівник — ПЕП"), default=False)

    legal_entity = models.BooleanField(
        _("Юрособа"), default=True)

    edrpou = models.CharField(
        _("ЄДРПОУ"), max_length=50, blank=True)

    zip_code = models.CharField(_("Індекс"), max_length=20, blank=True)
    city = models.CharField(_("Місто"), max_length=255, blank=True)
    street = models.CharField(_("Вулиця"), max_length=100, blank=True)
    appt = models.CharField(_("№ будинку, офісу"), max_length=50, blank=True)
    raw_address = models.TextField(_('"Сира" адреса'), blank=True)

    wiki = RedactorField(_("Вікі-стаття"), blank=True)

    other_founders = RedactorField(
        _("Інші засновники"),
        help_text=_("Через кому, не PEP"), blank=True)

    other_recipient = models.CharField(
        _("Бенефіціарій"), help_text=_("Якщо не є PEPом"), blank=True,
        max_length=200)

    other_owners = RedactorField(
        _("Інші власники"),
        help_text=_("Через кому, не PEP"), blank=True)

    other_managers = RedactorField(
        _("Інші керуючі"),
        help_text=_("Через кому, не PEP"), blank=True)

    bank_name = RedactorField(_("Фінансова інформація"), blank=True)

    sanctions = RedactorField(_("Санкції"), blank=True)

    related_companies = models.ManyToManyField(
        "self", through="Company2Company", symmetrical=False)

    last_change = models.DateTimeField(
        _("Дата останньої зміни профіля або зв'язків профіля"), blank=True, null=True
    )

    last_editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_("Автор зміни"),
        blank=True,
        null=True,
    )

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
            for i in self.from_persons.prefetch_related("from_person")]

        d["related_countries"] = [
            i.to_dict()
            for i in self.from_countries.prefetch_related("to_country")]

        d["related_companies"] = [
            i.to_dict()
            for i in self.to_companies.prefetch_related("to_company")] + [
            i.to_dict_reverse()
            for i in self.from_companies.prefetch_related("from_company")
        ]

        d["status"] = self.get_status_display()
        d["status_en"] = translate_into(self.get_status_display())
        d["founded"] = self.founded_human
        d["closed"] = self.closed_on_human

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
            edrpou_chunks = list(filter(
                None,
                map(unicode.strip, re.split('([a-z]+)', self.edrpou, flags=re.IGNORECASE))
            ))

            suggestions += edrpou_chunks
            suggestions.append(self.edrpou.lstrip("0"))

            if self.edrpou.isdigit():
                suggestions.append(self.edrpou.rjust(8, "0"))

            d["code_chunks"] = edrpou_chunks

        d["name_suggest"] = [
            {"input": x} for x in set(suggestions)
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
                term__iexact=lookup_term(self.short_name_uk)).first()

            if t and t.translation:
                self.short_name_en = t.translation

        edrpou = self.edrpou or ""
        if " " in edrpou and edrpou.strip() and ":" not in edrpou:
            self.edrpou = self.edrpou.replace(" ", "")

        super(Company, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("company_details", kwargs={"company_id": self.pk})

    def localized_url(self, locale):
        curr_lang = get_language()
        activate(locale)
        url = self.get_absolute_url()
        activate(curr_lang)
        return url

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    @property
    def all_related_persons(self):
        related_persons = [
            (i.relationship_type_uk, deepcopy(i.from_person), i)
            for i in self.from_persons.prefetch_related("from_person").defer(
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
            "bank_customers": [],
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

            elif rtp.lower() in ["клієнт банку"]:
                res["bank_customers"].append(p)
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
            (i.relationship_type, deepcopy(i.to_country), i)
            for i in self.from_countries.prefetch_related("to_country")
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

    # TODO: Request in bulk in all_related_companies?
    @property
    def foreign_registration(self):
        return self.from_countries.prefetch_related("to_country").filter(
            relationship_type="registered_in").exclude(to_country__iso2="UA")

    @property
    def all_related_companies(self):
        related_companies = [
            (i.relationship_type, deepcopy(i.to_company), i)
            for i in self.to_companies.prefetch_related("to_company").defer(
                "to_company__wiki",
                "to_company__other_founders",
                "to_company__other_recipient",
                "to_company__other_owners",
                "to_company__other_managers",
                "to_company__bank_name",
                "to_company__sanctions",
            )
        ] + [
            (i.reverse_relationship_type, deepcopy(i.from_company), i)
            for i in self.from_companies.prefetch_related("from_company").defer(
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
            "banks": [],
            "all": []
        }

        for rtp, p, rel in sorted(related_companies, key=lambda x: x[1].name_uk):
            p.rtype = rtp
            p.connection = rel

            if rtp in ["Засновник", "Співзасновник",
                       "Колишній власник/засновник",
                       "Колишній співвласник/співзасновник"]:
                res["founders"].append(p)
            elif rtp == "Клієнт банку":
                res["banks"].append(p)
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
                    "relation": unicode(ugettext_lazy(c.rtype or "")),
                    "node": c.get_node_info(False),
                    "model": c.connection._meta.model_name,
                    "pk": c.connection.pk
                })

            countries = self.from_countries.prefetch_related("to_country")
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
        verbose_name = _("Юридична особа")
        verbose_name_plural = _("Юридичні особи")

        permissions = (
            ("export_companies", "Can export the dataset of companies"),
        )

