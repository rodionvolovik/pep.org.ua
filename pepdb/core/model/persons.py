# coding: utf-8
from __future__ import unicode_literals

from itertools import chain
from copy import deepcopy

import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_noop as _
from django.utils.translation import ugettext_lazy, activate, get_language
from django.forms.models import model_to_dict
from django.conf import settings
from django.db.models.functions import Coalesce
from django.db.models import Q, Value
from django.contrib.auth.models import User

from core.fields import RedactorField
from translitua import translitua
import select2.fields
import select2.models

from core.model.base import AbstractNode
from core.model.translations import Ua2EnDictionary
from core.utils import render_date, lookup_term, parse_fullname, translate_into
from core.model.declarations import Declaration

# to_*_dict methods are used to convert two main entities that we have, Person
# and Company into document indexable by ElasticSearch.
# Links between Persons, Person and Company, Companies, Person and Country,
# Company and Country is also converted to subdocuments and attached to
# Person/Company documents. Because Person and Company needs different
# subdocuments, Person2Company has two different methods, to_person_dict and
# to_company_dict. For the same reason Person2Person and Company2Company has
# to_dict/to_dict_reverse because same link provides info to both persons.


class Person(models.Model, AbstractNode):
    _reasons_of_termination = (
        (1, _("Помер")),
        (2, _("Звільнився/склав повноваження")),
        (3, _("Пов'язана особа або член сім'ї - ПЕП помер")),
        (4, _("Пов'язана особа або член сім'ї - ПЕП припинив бути ПЕПом")),
        (5, _("Зміни у законодавстві що визначає статус ПЕПа")),
        (6, _("Зміни форми власності юр. особи посада в котрій давала статус ПЕПа")),
    )

    _types_of_officials = (
        (1, _("Національний публічний діяч")),
        (2, _("Іноземний публічний діяч")),
        (3,
         _("Діяч, що виконуює значні функції в міжнародній організації")),
        (4, _("Пов'язана особа")),
        (5, _("Член сім'ї")),
    )

    last_name = models.CharField("Прізвище", max_length=40)
    first_name = models.CharField("Ім'я", max_length=40)
    patronymic = models.CharField("По батькові", max_length=40, blank=True)

    publish = models.BooleanField("Опублікувати", default=False)
    is_pep = models.BooleanField("Є PEPом", default=True)
    imported = models.BooleanField("Був імпортований з гугл-таблиці",
                                   default=False)

    photo = models.ImageField("Світлина", blank=True, upload_to="images")
    dob = models.DateField("Дата народження", blank=True, null=True)
    dob_details = models.IntegerField(
        "Дата народження: точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    city_of_birth = models.CharField(
        "Місто народження", max_length=100, blank=True)

    related_countries = models.ManyToManyField(
        "Country", verbose_name="Пов'язані країни",
        through="Person2Country", related_name="people")

    reputation_assets = RedactorField(
        "Статки", blank=True)

    reputation_sanctions = RedactorField(
        "Наявність санкцій", blank=True)
    reputation_crimes = RedactorField(
        "Кримінальні провадження", blank=True)
    reputation_manhunt = RedactorField(
        "Перебування у розшуку", blank=True)
    reputation_convictions = RedactorField(
        "Наявність судимості", blank=True)

    related_persons = select2.fields.ManyToManyField(
        "self", through="Person2Person", symmetrical=False,
        ajax=True,
        search_field=(
            lambda q: Q(last_name__icontains=q) | Q(first_name__icontains=q)))

    related_companies = models.ManyToManyField(
        "Company", through="Person2Company")

    wiki = RedactorField("Вікі-стаття", blank=True)
    wiki_draft = RedactorField("Чернетка вікі-статті", blank=True)
    names = models.TextField("Варіанти написання імені", blank=True)

    also_known_as = models.TextField("Інші імена", blank=True)

    type_of_official = models.IntegerField(
        "Тип ПЕП",
        choices=_types_of_officials,
        blank=True,
        null=True)

    risk_category = models.CharField(
        "Рівень ризику",
        choices=(
            ("danger", _("Неприйнятно високий")),
            ("high", _("Високий")),
            ("medium", _("Середній")),
            ("low", _("Низький")),
        ),
        max_length=6, default="low")

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    hash = models.CharField("Хеш", max_length=40, blank=True)

    reason_of_termination = models.IntegerField(
        "Причина припинення статусу ПЕП",
        choices=_reasons_of_termination,
        blank=True,
        null=True)

    termination_date = models.DateField(
        "Дата припинення статусу ПЕП", blank=True, null=True,
        help_text="Вказується реальна дата зміни без врахування 3 років (реальна дата звільнення, тощо)"
    )
    termination_date_details = models.IntegerField(
        "Дата припинення статусу ПЕП: точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0
    )

    last_change = models.DateTimeField(
        "Дата останньої зміни профіля або зв'язків профіля", blank=True, null=True
    )

    last_editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Автор зміни",
        blank=True,
        null=True,
    )


    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "last_name__icontains", "first_name__icontains")

    def __unicode__(self):
        return "%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    @property
    def date_of_birth(self):
        return render_date(self.dob, self.dob_details)

    def _last_workplace(self):
        # Looking for a most recent appointment that has at least one date set
        # It'll work in following three cases:
        # Case 1: date_finished=null, date_established is the most recent one
        # i.e person got appointed and still holds the office
        # else
        # Case 2: date_finished=is the most recent one
        # and the date_established is the most recent one or null
        # i.e person got appointed and then resigned.

        # Tricky part: null values in dates are getting on top of the list when
        # you are sorting in decreasing order. So without exclude clause this
        # query will return the positions without both dates on the top of the
        # list
        qs = self.person2company_set.order_by(
            "-is_employee", "-date_finished", "-date_established") \
            .exclude(
                date_finished__isnull=True,  # AND!
                date_established__isnull=True) \
            .exclude(relationship_type_uk="Клієнт банку") \
            .prefetch_related("to_company") \
            .only(
                "to_company__short_name_uk", "to_company__name_uk",
                "to_company__short_name_en", "to_company__name_en",
                "to_company__id",
                "relationship_type_uk", "relationship_type_en")

        if qs:
            return qs

        # If nothing is found we are going to return the position that
        # has finished date set to null or the most recent one.
        # In contrast with previous query it'll also return those positions
        # where date_finished and date_established == null.
        qs = self.person2company_set.order_by(
            "-is_employee", "-date_finished").prefetch_related("to_company") \
            .exclude(relationship_type_uk="Клієнт банку") \
            .only(
                "to_company__short_name_uk", "to_company__name_uk",
                "to_company__short_name_en", "to_company__name_en",
                "to_company__id",
                "relationship_type_uk", "relationship_type_en")

        return qs

    def _last_workplace_from_declaration(self):
        return Declaration.objects.filter(person=self, confirmed="a").order_by(
            "-nacp_declaration", "-year").only(
            "year", "office_en", "position_en", "office_uk", "position_uk", "url")[:1]

    @property
    def last_workplace(self):
        qs = self._last_workplace()
        if qs:
            l = qs[0]
            return {
                "company": l.to_company.short_name_uk or l.to_company.name_uk,
                "company_id": l.to_company.pk,
                "position": l.relationship_type_uk
            }
        else:
            qs = self._last_workplace_from_declaration()
            if qs:
                d = qs[0]
                return {
                    "company": d.office_uk,
                    "company_id": None,
                    "position": d.position_uk
                }

        return ""

    # Fuuugly hack
    @property
    def last_workplace_en(self):
        qs = self._last_workplace()
        if qs:
            l = qs[0]

            return {
                "company": l.to_company.short_name_en or l.to_company.name_en,
                "company_id": l.to_company.pk,
                "position": l.relationship_type_en
            }
        else:
            qs = self._last_workplace_from_declaration()
            if qs:
                d = qs[0]
                return {
                    "company": d.office_en,
                    "company_id": None,
                    "position": d.position_en
                }

        return ""

    # Fuuugly hack
    @property
    def translated_last_workplace(self):
        qs = self._last_workplace()
        if qs:
            l = qs[0]

            return {
                "company": l.to_company.short_name or l.to_company.name,
                "company_id": l.to_company.pk,
                "position": l.relationship_type
            }
        else:
            qs = self._last_workplace_from_declaration()
            if qs:
                d = qs[0]
                return {
                    "company": d.office,
                    "company_id": None,
                    "position": d.position
                }

        return ""

    @property
    def workplaces(self):
        # Coalesce works by taking the first non-null value.  So we give it
        # a date far before any non-null values of last_active.  Then it will
        # naturally sort behind instances of Box with a non-null last_active
        # value.
        # djangoproject.com/en/1.8/ref/models/database-functions/#coalesce
        the_past = datetime.datetime.now() - datetime.timedelta(days=10 * 365)

        timeline = self.person2company_set.prefetch_related(
            "to_company", "proofs", "proofs__proof_document").filter(is_employee=True).annotate(
                fixed_date_established=Coalesce(
                    'date_established', Value(the_past))
        ).order_by('-fixed_date_established')

        return timeline

    @property
    def assets(self):
        return self.person2company_set.prefetch_related("to_company", "proofs", "proofs__proof_document").filter(
            is_employee=False,
            relationship_type_uk__in=(
                "Член центрального статутного органу",
                "Повірений у справах",
                "Засновник/учасник",
                "Колишній засновник/учасник",
                "Бенефіціарний власник",
                "Номінальний власник",
                "Номінальний директор",
                "Фінансові зв'язки",
                "Секретар",
                "Керуючий",
                "Контролер",
            ))

    @property
    def all_related_companies(self):
        companies = self.person2company_set.prefetch_related(
            "to_company", "proofs", "proofs__proof_document").filter(is_employee=False)

        banks = []
        rest = []
        for c in companies:
            if c.relationship_type_uk == "Клієнт банку":
                banks.append(c)
            else:
                rest.append(c)

        return {
            "banks": banks,
            "rest": rest
        }

    @property
    def all_related_persons(self):
        related_persons = [
            (i.to_relationship_type, i.from_relationship_type, deepcopy(i.to_person), i)
            for i in self.to_persons.prefetch_related("to_person", "proofs", "proofs__proof_document").defer(
                "to_person__reputation_assets",
                "to_person__reputation_sanctions",
                "to_person__reputation_crimes",
                "to_person__reputation_manhunt",
                "to_person__reputation_convictions",
                "to_person__wiki",
                "to_person__names",
                "to_person__hash"
            )
        ] + [
            (i.from_relationship_type, i.to_relationship_type,
             deepcopy(i.from_person), i)
            for i in self.from_persons.prefetch_related("from_person", "proofs", "proofs__proof_document").defer(
                "from_person__reputation_assets",
                "from_person__reputation_sanctions",
                "from_person__reputation_crimes",
                "from_person__reputation_manhunt",
                "from_person__reputation_convictions",
                "from_person__wiki",
                "from_person__names",
                "from_person__hash"
            )
        ]

        res = {
            "family": [],
            "personal": [],
            "business": [],
            "all": []
        }

        for rtp, rrtp, p, rel in related_persons:
            p.rtype = rtp
            p.reverse_rtype = rrtp
            p.connection = rel

            if rtp in ["особисті зв'язки"]:
                res["personal"].append(p)
            elif rtp in ["ділові зв'язки"]:
                res["business"].append(p)
            else:
                res["family"].append(p)

            res["all"].append(p)

        return res

    @property
    def parsed_names(self):
        return filter(None, self.names.split("\n"))

    @property
    def full_name(self):
        return ("%s %s %s" % (self.first_name, self.patronymic,
                              self.last_name)).replace("  ", " ")

    @property
    def full_name_en(self):
        return ("%s %s %s" % (self.first_name_en, self.patronymic_en,
                              self.last_name_en)).replace("  ", " ")

    def to_dict(self):
        """
        Convert Person model to an indexable presentation for ES.
        """
        d = model_to_dict(self, fields=[
            "id", "last_name", "first_name", "patronymic", "dob",
            "last_name_en", "first_name_en", "patronymic_en",
            "dob_details", "is_pep", "names",
            "wiki_uk", "wiki_en",
            "city_of_birth_uk", "city_of_birth_en",
            "reputation_sanctions_uk", "reputation_sanctions_en",
            "reputation_convictions_uk", "reputation_convictions_en",
            "reputation_assets_uk", "reputation_assets_en",
            "reputation_crimes_uk", "reputation_crimes_en",
            "reputation_manhunt_uk", "reputation_manhunt_en",
            "also_known_as_uk", "also_known_as_en"
        ])

        d["related_persons"] = [
            i.to_dict()
            for i in self.to_persons.prefetch_related("to_person")] + [
            i.to_dict_reverse()
            for i in self.from_persons.prefetch_related("from_person")
        ]
        d["related_countries"] = [
            i.to_dict()
            for i in self.person2country_set.prefetch_related("to_country")]
        d["related_companies"] = [
            i.to_company_dict()
            for i in self.person2company_set.prefetch_related("to_company")]

        d["declarations"] = [
            i.to_dict()
            for i in Declaration.objects.filter(
                person=self,
                confirmed="a"
            )
        ]

        d["photo"] = settings.SITE_URL + self.photo.url if self.photo else ""
        d["photo_path"] = self.photo.name if self.photo else ""
        d["date_of_birth"] = self.date_of_birth

        last_workplace = self.last_workplace
        if last_workplace:
            d["last_workplace"] = last_workplace["company"]
            d["last_job_title"] = last_workplace["position"]
            d["last_job_id"] = last_workplace["company_id"]

            last_workplace_en = self.last_workplace_en
            d["last_workplace_en"] = last_workplace_en["company"]
            d["last_job_title_en"] = last_workplace_en["position"]

        d["type_of_official"] = self.get_type_of_official_display()

        d["type_of_official_en"] = translate_into(
            self.get_type_of_official_display(), "en"
        )

        d["full_name"] = self.full_name
        d["full_name_en"] = self.full_name_en

        def generate_suggestions(last_name, first_name, patronymic, *args):
            if not last_name:
                return []

            return [
                {
                    "input": " ".join([last_name, first_name, patronymic]),
                    "weight": 5,
                },
                {
                    "input": " ".join([first_name, patronymic, last_name]),
                    "weight": 2,
                },
                {
                    "input": " ".join([first_name, last_name]),
                    "weight": 2,
                }
            ]

        input_variants = [generate_suggestions(
            d["last_name"], d["first_name"], d["patronymic"])]

        input_variants += list(map(
            lambda x: generate_suggestions(*parse_fullname(x)),
            self.parsed_names
        ))

        d["full_name_suggest"] = list(chain.from_iterable(input_variants))

        d["_id"] = d["id"]

        return d

    def get_absolute_url(self):
        return reverse("person_details", kwargs={"person_id": self.pk})

    def localized_url(self, locale):
        curr_lang = get_language()
        activate(locale)
        url = self.get_absolute_url()
        activate(curr_lang)
        return url

    # TODO: Request in bulk in all_related_persons?
    @property
    def foreign_citizenship(self):
        return self.person2country_set.prefetch_related("to_country").filter(
            relationship_type__in=["citizenship", "registered_in"]).exclude(to_country__iso2="UA")

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    def save(self, *args, **kwargs):
        if self.first_name_uk:
            self.first_name_en = translitua(self.first_name_uk)
        else:
            self.first_name_en = ""

        if self.last_name_uk:
            self.last_name_en = translitua(self.last_name_uk)
        else:
            self.last_name_en = ""

        if self.patronymic_uk:
            self.patronymic_en = translitua(self.patronymic_uk)
        else:
            self.patronymic_en = ""

        if self.also_known_as_uk:
            self.also_known_as_en = translitua(self.also_known_as_uk)
        else:
            self.also_known_as_en = ""

        if self.city_of_birth_uk and not self.city_of_birth_en:
            t = Ua2EnDictionary.objects.filter(
                term__iexact=lookup_term(self.city_of_birth_uk)).first()

            if t and t.translation:
                self.city_of_birth_en = t.translation

        super(Person, self).save(*args, **kwargs)

    def get_declarations(self):
        decls = Declaration.objects.filter(
            person=self, confirmed="a").order_by("year", "nacp_declaration")

        corrected = []
        res = []
        # Filtering out original declarations, if there are
        # also corrected one
        for d in decls:
            if not d.nacp_declaration:
                continue

            if d.source["intro"].get("corrected"):
                corrected.append(
                    (d.year, d.source["intro"].get("doc_type"))
                )

        for d in decls:
            if d.nacp_declaration and not d.source["intro"].get("corrected"):
                if (d.year, d.source["intro"].get("doc_type")) in corrected:
                    continue

            res.append(d)

        return res

    def get_node_info(self, with_connections=False):
        res = super(Person, self).get_node_info(with_connections)
        res["name"] = self.full_name

        last_workplace = self.translated_last_workplace
        if last_workplace:
            res["description"] = "{position} @ {company}".format(
                **last_workplace)
        res["kind"] = unicode(
            ugettext_lazy(self.get_type_of_official_display() or ""))

        if with_connections:
            connections = []

            # Because of a complicated logic here we are piggybacking on
            # existing method that handles both directions of relations
            for p in self.all_related_persons["all"]:
                connections.append({
                    "relation": unicode(ugettext_lazy(p.rtype)),
                    "node": p.get_node_info(False),
                    "model": p.connection._meta.model_name,
                    "pk": p.connection.pk
                })

            companies = self.person2company_set.prefetch_related("to_company")
            for c in companies:
                connections.append({
                    "relation": unicode(c.relationship_type),
                    "node": c.to_company.get_node_info(False),
                    "model": c._meta.model_name,
                    "pk": c.pk
                })

            countries = self.person2country_set.prefetch_related("to_country")
            for c in countries:
                connections.append({
                    "relation": unicode(c.relationship_type),
                    "node": c.to_country.get_node_info(False),
                    "model": c._meta.model_name,
                    "pk": c.pk
                })

            res["connections"] = connections

        return res

    class Meta:
        verbose_name = "Фізична особа"
        verbose_name_plural = "Фізичні особи"

        index_together = [
            ["last_name", "first_name"],
        ]

        permissions = (
            ("export_persons", "Can export the dataset"),
        )
