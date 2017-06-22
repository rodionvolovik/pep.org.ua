# coding: utf-8
from __future__ import unicode_literals
from itertools import chain
from copy import copy
import datetime
from collections import OrderedDict, defaultdict

from django.db import models
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Coalesce, Value
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import ArrayField

# Strange bug related to babel
from django.utils.translation import ugettext_noop as _
from django.utils.translation import ugettext_lazy, activate, deactivate

from translitua import translitua
from jsonfield import JSONField
import select2.fields
import select2.models
from redactor.fields import RedactorField

from core.utils import (
    parse_fullname, parse_family_member, RELATIONS_MAPPING, render_date,
    lookup_term)


class AbstractNode(object):
    def get_node_info(self, with_connections=False):
        t = type(self)
        if t._deferred:
            t = t.__base__

        return {
            "pk": self.pk,
            "model": t._meta.model_name,
            "details": reverse(
                "connections",
                kwargs={
                    "model": t._meta.model_name,
                    "obj_id": self.pk
                }
            ),
            "kind": "",
            "description": "",
            "connections": []
        }

# to_*_dict methods are used to convert two main entities that we have, Person
# and Company into document indexable by ElasticSearch.
# Links between Persons, Person and Company, Companies, Person and Country,
# Company and Country is also converted to subdocuments and attached to
# Person/Company documents. Because Person and Company needs different
# subdocuments, Person2Company has two different methods, to_person_dict and
# to_company_dict. For the same reason Person2Person and Company2Company has
# to_dict/to_dict_reverse because same link provides info to both persons.


class Person(models.Model, AbstractNode):
    last_name = models.CharField("Прізвище", max_length=40)
    first_name = models.CharField("Ім'я", max_length=40)
    patronymic = models.CharField("По-батькові", max_length=40, blank=True)

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
        "Кримінальні впровадження", blank=True)
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
    names = models.TextField("Варіанти написання імені", blank=True)

    also_known_as = models.TextField("Інші імена", blank=True)

    type_of_official = models.IntegerField(
        "Тип ПЕП",
        choices=(
            (1, _("Національний публічний діяч")),
            (2, _("Іноземний публічний діяч")),
            (3,
             _("Діяч, що виконуює значні функції в міжнародній організації")),
            (4, _("Пов'язана особа")),
            (5, _("Близька особа")),
        ),
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
            "-is_employee", "-date_finished",
            "-date_established").exclude(
                date_finished__isnull=True,  # AND!
                date_established__isnull=True).select_related("to_company")

        if qs:
            return qs

        # If nothing is found we are going to return the position that
        # has finished date set to null or the most recent one.
        # In contrast with previous query it'll also return those positions
        # where date_finished and date_established == null.
        qs = self.person2company_set.order_by(
            "-is_employee", "-date_finished").select_related("to_company")

        return qs

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

        return ""

    @property
    def workplaces(self):
        # Coalesce works by taking the first non-null value.  So we give it
        # a date far before any non-null values of last_active.  Then it will
        # naturally sort behind instances of Box with a non-null last_active
        # value.
        # djangoproject.com/en/1.8/ref/models/database-functions/#coalesce
        the_past = datetime.datetime.now() - datetime.timedelta(days=10 * 365)

        timeline = self.person2company_set.select_related(
            "to_company").filter(is_employee=True).annotate(
                fixed_date_established=Coalesce(
                    'date_established', Value(the_past))
        ).order_by('-fixed_date_established')

        return timeline

    @property
    def assets(self):
        return self.person2company_set.select_related("to_company").filter(
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
        # TODO: unify output format with all_related_persons
        # TODO: adjust name to reflect that it's only a subset of companies
        companies = self.person2company_set.select_related(
            "to_company").filter(is_employee=False)

        assets = []
        related = []
        for c in companies:
            if c.relationship_type_uk.lower() in (
                    "член центрального статутного органу",
                    "повірений у справах",
                    "засновник/учасник",
                    "колишній засновник/учасник",
                    "бенефіціарний власник",
                    "номінальний власник",
                    "номінальний директор",
                    "фінансові зв'язки",
                    "секретар",  # ???
                    "керуючий",
                    "контролер"):
                assets.append(c)
            else:
                related.append(c)

        return assets, related

    @property
    def all_related_persons(self):
        related_persons = [
            (i.to_relationship_type, i.from_relationship_type, i.to_person, i)
            for i in self.to_persons.select_related("to_person").defer(
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
             i.from_person, i)
            for i in self.from_persons.select_related("from_person").defer(
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
        ])

        d["related_persons"] = [
            i.to_dict()
            for i in self.to_persons.select_related("to_person")] + [
            i.to_dict_reverse()
            for i in self.from_persons.select_related("from_person")
        ]
        d["related_countries"] = [
            i.to_dict()
            for i in self.person2country_set.select_related("to_country")]
        d["related_companies"] = [
            i.to_company_dict()
            for i in self.person2company_set.select_related("to_company")]
        d["declarations"] = [
            i.to_dict()
            for i in Declaration.objects.filter(
                person=self,
                confirmed="a",
                nacp_declaration=False
            )
        ]

        d["photo"] = self.photo.name if self.photo else ""
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
        d["risk_category"] = self.get_risk_category_display()
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
        activate(locale)
        url = self.get_absolute_url()
        deactivate()
        return url

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    def save(self, *args, **kwargs):
        self.first_name_en = translitua(self.first_name_uk)
        self.last_name_en = translitua(self.last_name_uk)
        self.patronymic_en = translitua(self.patronymic_uk)
        self.also_known_as_en = translitua(self.also_known_as_uk)

        super(Person, self).save(*args, **kwargs)

    def declarations_extra_fields(self):
        for decl in self.declaration_extras:
            pass

    def get_declarations(self):
        decls = Declaration.objects.filter(
            person=self, confirmed="a").order_by("year")

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
            ugettext_lazy(self.get_type_of_official_display()) or "")

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

            companies = self.person2company_set.select_related("to_company")
            for c in companies:
                connections.append({
                    "relation": unicode(c.relationship_type),
                    "node": c.to_company.get_node_info(False),
                    "model": c._meta.model_name,
                    "pk": c.pk
                })

            countries = self.person2country_set.select_related("to_country")
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


class AbstractRelationship(models.Model):
    date_established = models.DateField(
        "Зв'язок почався", blank=True, null=True)

    date_established_details = models.IntegerField(
        "точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    date_finished = models.DateField(
        "Зв'язок скінчився", blank=True, null=True)

    date_finished_details = models.IntegerField(
        "точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    date_confirmed = models.DateField(
        "Підтверджено", blank=True, null=True)

    date_confirmed_details = models.IntegerField(
        "точність",
        choices=(
            (0, "Точна дата"),
            (1, "Рік та місяць"),
            (2, "Тільки рік"),
        ),
        default=0)

    @property
    def date_established_human(self):
        return render_date(self.date_established,
                           self.date_established_details)

    @property
    def date_finished_human(self):
        return render_date(self.date_finished,
                           self.date_finished_details)

    @property
    def date_confirmed_human(self):
        return render_date(self.date_confirmed,
                           self.date_confirmed_details)

    proof_title = models.TextField(
        "Назва доказу зв'язку", blank=True,
        help_text="Наприклад: склад ВР 7-го скликання")
    proof = models.TextField("Посилання на доказ зв'язку", blank=True)

    @property
    def has_additional_info(self):
        return any([
            self.date_confirmed, self.date_established, self.date_finished,
            self.proof, self.proof_title])

    class Meta:
        abstract = True


class Person2Person(AbstractRelationship):
    _relationships_explained = OrderedDict([
        (_("чоловік"), [_("дружина")]),
        (_("дружина"), [_("чоловік")]),
        (_("чоловік/дружина"), [_("чоловік/дружина")]),
        (_("батько"), [_("син"), _("дочка"), _("син/дочка")]),
        (_("мати"), [_("син"), _("дочка"), _("син/дочка")]),
        (_("батько/мати"), [_("син"), _("дочка"), _("син/дочка")]),
        (_("син"), [_("батько"), _("мати"), _("батько/мати")]),
        (_("дочка"), [_("батько"), _("мати"), _("батько/мати")]),
        (_("син/дочка"), [_("батько"), _("мати"), _("батько/мати")]),
        (_("вітчим"), [_("пасинок"), _("падчерка")]),
        (_("мачуха"), [_("пасинок"), _("падчерка")]),
        (_("пасинок"), [_("вітчим"), _("мачуха")]),
        (_("падчерка"), [_("вітчим"), _("мачуха")]),
        (_("рідний брат"), [_("рідна сестра"), _("рідний брат")]),
        (_("рідна сестра"), [_("рідна сестра"), _("рідний брат")]),
        (_("дід"), [_("внук"), _("внучка")]),
        (_("баба"), [_("внук"), _("внучка")]),
        (_("прадід"), [_("правнук"), _("правнучка")]),
        (_("прабаба"), [_("правнук"), _("правнучка")]),
        (_("внук"), [_("дід"), _("баба")]),
        (_("внучка"), [_("дід"), _("баба")]),
        (_("правнук"), [_("прадід"), _("прабаба")]),
        (_("правнучка"), [_("прадід"), _("прабаба")]),
        (_("зять"), [_("теща"), _("тесть")]),
        (_("невістка"), [_("свекор"), _("свекруха")]),
        (_("тесть"), [_("зять")]),
        (_("теща"), [_("зять")]),
        (_("свекор"), [_("невістка")]),
        (_("свекруха"), [_("невістка")]),
        (_("усиновлювач"), [_("усиновлений")]),
        (_("усиновлений"), [_("усиновлювач")]),
        (_("опікун чи піклувальник"),
         [_("особа, яка перебуває під опікою або піклуванням")]),
        (_("особа, яка перебуває під опікою або піклуванням"),
         [_("опікун чи піклувальник")]),
        (_("особи, які спільно проживають"),
         [_("особи, які спільно проживають")]),
        (_("пов'язані спільним побутом і мають взаємні права та обов'язки"),
         [_("пов'язані спільним побутом і мають взаємні права та обов'язки")]),
        (_("ділові зв'язки"), [_("ділові зв'язки")]),
        (_("особисті зв'язки"), [_("особисті зв'язки")]),
    ])

    from_person = models.ForeignKey(
        "Person", verbose_name="Персона 1", related_name="to_persons")
    to_person = models.ForeignKey(
        "Person", verbose_name="Персона 2", related_name="from_persons")

    from_relationship_type = models.CharField(
        "Персона 1 є",
        choices=(zip(_relationships_explained.keys(),
                     map(_, _relationships_explained.keys()))),
        max_length=100,
        blank=True)

    to_relationship_type = models.CharField(
        "Персона 2 є",
        choices=(zip(_relationships_explained.keys(),
                     map(_, _relationships_explained.keys()))),
        max_length=100,
        blank=True)

    declaration = models.ForeignKey(
        "Declaration", blank=True, null=True,
        verbose_name="Декларація, що підтверджує зв'язок")

    declarations = ArrayField(
        models.IntegerField(),
        verbose_name="Декларації, що підтверджують зв'язок",
        null=True,
        blank=True
    )

    def __unicode__(self):
        return "%s (%s) -> %s (%s)" % (
            self.from_person, self.get_from_relationship_type_display(),
            self.to_person, self.get_to_relationship_type_display())

    def to_dict(self):
        """
        Convert link between two persons into indexable presentation.
        """
        return {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,

            "relationship_type": self.to_relationship_type,
            "is_pep": self.to_person.is_pep,
            "person_uk": "%s %s %s" % (
                self.to_person.first_name_uk,
                self.to_person.patronymic_uk,
                self.to_person.last_name_uk),
            "person_en": "%s %s %s" % (
                self.to_person.first_name_en,
                self.to_person.patronymic_en,
                self.to_person.last_name_en),
        }

    def to_dict_reverse(self):
        """
        Convert back link between two persons to indexable presentation.
        """
        return {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,

            "relationship_type": self.from_relationship_type,
            "is_pep": self.from_person.is_pep,
            "person_uk": "%s %s %s" % (
                self.from_person.first_name_uk,
                self.from_person.patronymic_uk,
                self.from_person.last_name_uk),
            "person_en": "%s %s %s" % (
                self.from_person.first_name_en,
                self.from_person.patronymic_en,
                self.from_person.last_name_en),
        }

    class Meta:
        verbose_name = "Зв'язок з іншою персоною"
        verbose_name_plural = "Зв'язки з іншими персонами"


class Person2Company(AbstractRelationship):
    _relationships_explained = [
        "Президент",
        "Прем’єр-міністр",
        "Міністр",
        "Перший заступник міністра",
        "Заступник міністра",
        "Керівник",
        "Перший заступник керівника",
        "Заступник керівника",
        "Народний депутат",
        "Голова",
        "Заступник Голови",
        "Член Правління",
        "Член Ради",
        "Суддя",
        "Член",
        "Генеральний прокурор",
        "Заступник Генерального прокурора",
        "Надзвичайний і повноважний посол",
        "Головнокомандувач",
        "Службовець першої категорії посад",
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
    ]

    from_person = models.ForeignKey("Person")
    to_company = models.ForeignKey(
        "Company", verbose_name="Компанія або установа",
        related_name="from_persons")

    relationship_type = models.TextField(
        "Тип зв'язку",
        blank=True)

    is_employee = models.BooleanField(
        "Працює(-вав)",
        default=False
    )

    def __unicode__(self):
        return "%s (%s)" % (
            self.to_company, self.relationship_type)

    def to_company_dict(self):
        return {
            "relationship_type_uk": self.relationship_type_uk,
            "relationship_type_en": self.relationship_type_en,

            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,

            "to_company_is_state": self.to_company.state_company,
            "to_company_edrpou": self.to_company.edrpou,
            "to_company_founded": self.to_company.founded_human,
            "to_company_uk": self.to_company.name_uk,
            "to_company_short_uk": self.to_company.short_name_uk,
            "to_company_en": self.to_company.name_en,
            "to_company_short_en": self.to_company.short_name_en
        }

    def to_person_dict(self):
        return {
            "relationship_type_uk": self.relationship_type_uk,
            "relationship_type_en": self.relationship_type_en,
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,

            "is_pep": self.from_person.is_pep,
            "person_uk": "%s %s %s" % (
                self.from_person.first_name_uk,
                self.from_person.patronymic_uk,
                self.from_person.last_name_uk),
            "person_en": "%s %s %s" % (
                self.from_person.first_name_en,
                self.from_person.patronymic_en,
                self.from_person.last_name_en),
        }

    def save(self, *args, **kwargs):
        if not self.relationship_type_en:
            t = Ua2EnDictionary.objects.filter(
                term__iexact=lookup_term(self.relationship_type_uk)).first()

            if t and t.translation:
                self.relationship_type_en = t.translation

        super(Person2Company, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Зв'язок з компанією/установою"
        verbose_name_plural = "Зв'язки з компаніями/установами"


class Company(models.Model, AbstractNode):
    name = models.CharField("Повна назва", max_length=512)
    short_name = models.CharField("Скорочена назва", max_length=50,
                                  blank=True)

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

    @property
    def founded_human(self):
        return render_date(self.founded,
                           self.founded_details)

    state_company = models.BooleanField(
        "Є державною установою", default=False)

    edrpou = models.CharField(
        "ЄДРПОУ/ідентифікаційний код", max_length=20, blank=True)

    zip_code = models.CharField("Індекс", max_length=10, blank=True)
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
            "other_managers", "bank_name"])

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
            )
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
                    "член правління", "член ради", "член", "директор",
                    "підписант", "номінальний директор", "керуючий"]:
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

        for rtp, p, rel in related_companies:
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

    class Meta:
        verbose_name = "Юридична особа"
        verbose_name_plural = "Юридичні особи"


class Company2Company(AbstractRelationship):
    _relationships_explained = [
        _("Власник"),
        _("Співвласник"),
        _("Споріднена"),
        _("Засновник"),
        _("Співзасновник"),
        _("Кредитор (фінансовий партнер)"),
        _("Надавач професійних послуг"),
        _("Клієнт"),
        _("Виконавець"),
        _("Замовник"),
        _("Підрядник"),
        _("Субпідрядник"),
        _("Постачальник"),
        _("Орендар"),
        _("Орендодавець"),
        _("Контрагент"),
        _("Правонаступник"),
        _("Правовласник"),
        _("Материнська компанія"),
        _("Дочірня компанія"),
        _("Член наглядового органу"),
        _("Колишній власник/засновник"),
        _("Колишній співвласник/співзасновник"),
    ]

    _relationships_mapping = {
        _("Власник"): _("Підконтрольна"),
        _("Співвласник"): _("Підконтрольна"),
        _("Колишній власник/засновник"): _("Підконтрольна"),
        _("Колишній співвласник/співзасновник"): _("Підконтрольна"),
        _("Споріднена"): _("Споріднена"),
        _("Засновник"): _("Підконтрольна"),
        _("Співзасновник"): _("Підконтрольна"),
        _("Кредитор (фінансовий партнер)"): _("Боржник, фінансовий партнер"),
        _("Надавач професійних послуг"): _("Отримувач професійних послуг"),
        _("Клієнт"): _("Надавач товарів/послуг"),
        _("Виконавець"): _("Замовник"),
        _("Замовник"): _("Виконавець"),
        _("Підрядник"): _("Замовник"),
        _("Субпідрядник"): _("Підрядник"),
        _("Постачальник"): _("Отримувач/покупець"),
        _("Орендар"): _("Орендодавець"),
        _("Орендодавець"): _("Орендар"),
        _("Контрагент"): _("Контрагент"),
        _("Правонаступник"): _("Попередник"),
        _("Правовласник"): _("Об'єкт правовласності"),
        _("Материнська компанія"): _("Дочірня компанія"),
        _("Дочірня компанія"): _("Материнська компанія"),
        _("Член наглядового органу)"): _("Підконтрольна")
    }

    from_company = models.ForeignKey("Company", related_name="to_companies")
    to_company = models.ForeignKey("Company", related_name="from_companies")

    relationship_type = models.CharField(
        "Тип зв'язку",
        choices=zip(_relationships_explained,
                    map(_, _relationships_explained)),
        max_length=30,
        blank=True)

    equity_part = models.FloatField(
        "Частка власності (відсотки)", blank=True, null=True)

    @property
    def reverse_relationship_type(self):
        return self._relationships_mapping.get(self.relationship_type)

    def to_dict(self):
        return {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "relationship_type": self.relationship_type,
            "state_company": self.to_company.state_company,
            "company": self.to_company.name
        }

    def to_dict_reverse(self):
        return {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "relationship_type": self.relationship_type,
            "state_company": self.from_company.state_company,
            "company": self.from_company.name
        }

    class Meta:
        verbose_name = "Зв'язок з компанією"
        verbose_name_plural = "Зв'язки з компаніями"


class Person2Country(AbstractRelationship):
    from_person = models.ForeignKey("Person", verbose_name="Персона")
    to_country = models.ForeignKey("Country", verbose_name="Країна")

    relationship_type = models.CharField(
        "Тип зв'язку",
        choices=(
            ("born_in", _("Народився(-лась)")),
            ("registered_in", _("Зареєстрований(-а)")),
            ("lived_in", _("Проживав(-ла)")),
            ("citizenship", _("Громадянин(-ка)")),
            ("business", _("Має зареєстрований бізнес")),
            ("realty", _("Має нерухомість")),
            ("under_sanctions", _("Під санкціями")),
        ),

        max_length=30,
        blank=False)

    def __unicode__(self):
        return "%s у %s" % (
            self.get_relationship_type_display(), self.to_country)

    def to_dict(self):
        return {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "relationship_type": self.relationship_type,
            "to_country_en": self.to_country.name_en,
            "to_country_uk": self.to_country.name_uk
        }

    class Meta:
        verbose_name = "Зв'язок з країною"
        verbose_name_plural = "Зв'язки з країнами"


class Company2Country(AbstractRelationship):
    from_company = models.ForeignKey(
        "Company", verbose_name="Компанія", related_name="from_countries")
    to_country = models.ForeignKey(
        "Country", verbose_name="Країна")

    relationship_type = models.CharField(
        "Тип зв'язку",
        choices=(
            ("registered_in", _("Зареєстрована")),
            ("under_sanctions", _("Під санкціями")),
        ),

        max_length=30,
        blank=False)

    def to_dict(self):
        return {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "relationship_type": self.relationship_type,
            "to_country_en": self.to_country.name_en,
            "to_country_uk": self.to_country.name_uk
        }

    def __unicode__(self):
        return "%s у %s" % (
            self.get_relationship_type_display(), self.to_country)

    class Meta:
        verbose_name = "Зв'язок з країною"
        verbose_name_plural = "Зв'язки з країнами"


class Country(models.Model, AbstractNode):
    name = models.CharField("Назва", max_length=100)
    iso2 = models.CharField("iso2 код", max_length=2, blank=True)
    iso3 = models.CharField("iso3 код", max_length=3, blank=True)
    is_jurisdiction = models.BooleanField("Не є країною", default=False)

    def __unicode__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name_en__icontains", "name_uk__icontains")

    def get_absolute_url(self):
        return reverse("countries", kwargs={"country_id": self.iso2})

    def localized_url(self, locale):
        activate(locale)
        url = self.get_absolute_url()
        deactivate()
        return url

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    class Meta:
        verbose_name = "Країна/юрісдикція"
        verbose_name_plural = "Країни/юрісдикції"

    def get_node_info(self, with_connections=False):
        res = super(Country, self).get_node_info(with_connections)
        res["name"] = self.name

        if with_connections:
            connections = []

            persons = self.person2country_set.select_related("from_person")
            for p in persons:
                connections.append({
                    "relation": unicode(
                        ugettext_lazy(p.get_relationship_type_display())),
                    "node": p.from_person.get_node_info(False),
                    "model": p._meta.model_name,
                    "pk": p.pk
                })

            companies = self.company2country_set.select_related("from_company")
            for c in companies:
                connections.append({
                    "relation": unicode(
                        ugettext_lazy(c.get_relationship_type_display())),
                    "node": c.from_company.get_node_info(False),
                    "model": c._meta.model_name,
                    "pk": c.pk
                })

            res["connections"] = connections

        return res


class Document(models.Model):
    doc = models.FileField("Файл", upload_to="documents", max_length=1000)
    name = models.CharField("Людська назва", max_length=255)
    uploaded = models.DateTimeField("Був завантажений", auto_now=True)
    source = models.CharField("Першоджерело", blank=True, max_length=255)
    uploader = models.ForeignKey(User, verbose_name="Хто завантажив",
                                 related_name="pep_document")
    hash = models.CharField("Хеш", max_length=40, blank=True)
    comments = models.TextField("Коментарі", blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документи"


class Ua2RuDictionary(models.Model):
    term = models.CharField("Термін", max_length=255, unique=True)
    translation = models.CharField(
        "Переклад російською", max_length=255, blank=True)
    alt_translation = models.CharField(
        "Альтернативний переклад", max_length=255, blank=True)
    comments = models.CharField("Коментарі", blank=True, max_length=100)

    def __unicode__(self):
        return self.term

    class Meta:
        verbose_name = "Переклад російською"
        verbose_name_plural = "Переклади російською"


class Ua2EnDictionary(models.Model):
    term = models.CharField("Термін", max_length=512, unique=True)
    translation = models.CharField(
        "Переклад англійською", max_length=512, blank=True)
    alt_translation = models.CharField(
        "Альтернативний переклад", max_length=512, blank=True)
    comments = models.CharField("Коментарі", blank=True, max_length=100)

    def __unicode__(self):
        return self.term

    class Meta:
        verbose_name = "Переклад англійською"
        verbose_name_plural = "Переклади англійською"
        unique_together = [
            ["term", "translation"],
        ]


class FeedbackMessage(models.Model):
    person = models.CharField(
        ugettext_lazy("Про кого"), max_length=150, blank=True)
    text = models.TextField(
        ugettext_lazy("Інформація"), blank=False)
    link = models.URLField(
        ugettext_lazy("Підтвердження"), max_length=512, blank=True)
    contacts = models.TextField(
        ugettext_lazy("Контакти"), max_length=512, blank=True)
    read = models.BooleanField(ugettext_lazy("Прочитано"), default=False)
    added = models.DateTimeField("Був надісланий", auto_now=True)

    class Meta:
        verbose_name = "Зворотній зв'язок"
        verbose_name_plural = "Зворотній зв'язок"


class Declaration(models.Model):
    STATUS_CHOICES = (
        ('p', 'Не перевірено'),
        ('r', 'Не підходить'),
        ('a', 'Опубліковано'),
        ('c', 'Перевірити'),
    )

    declaration_id = models.CharField(
        "Ідентифікатор", max_length=50, db_index=True)

    last_name = models.CharField("Прізвище", max_length=40)
    first_name = models.CharField("Ім'я", max_length=40)
    patronymic = models.CharField("По-батькові", max_length=40, blank=True)
    position = models.CharField("Посада", max_length=512, blank=True)
    office = models.CharField("Відомство", max_length=512, blank=True)
    region = models.CharField("Регіон", max_length=50, blank=True)
    year = models.CharField("Рік", max_length=4, blank=True, db_index=True)
    source = JSONField()
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
                    except ValueError:
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
                                "подарунок у негрошовій формі", "подарунок у грошовій формі",
                                "благодійна допомога", "приз"]:
                            continue

                        person = income.get("person", "1")
                        income_size = float(income.get("sizeIncome", "0"))

                        if person == "1":
                            resp["gifts_of_declarant"] += income_size
                        else:
                            resp["gifts_of_family"] += income_size
                    except ValueError:
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
                    except ValueError:
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

    class Meta:
        verbose_name = "Декларація"
        verbose_name_plural = "Декларації"


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


class ActionLog(models.Model):
    user = models.ForeignKey(User, verbose_name="Користувач")
    action = models.CharField(verbose_name="Дія", max_length=30)
    timestamp = models.DateTimeField(
        verbose_name="Дата та час", auto_now_add=True)
    details = models.TextField(verbose_name="Деталі", blank=True)

    class Meta:
        verbose_name = "Дія користувача"
        verbose_name_plural = "Дії користувачів"

        index_together = [
            ["user", "action", "timestamp"],
        ]
