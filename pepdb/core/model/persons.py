# coding: utf-8
from __future__ import unicode_literals

from itertools import chain
from copy import deepcopy
from urlparse import urlparse

import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_lazy, activate, get_language
from django.forms.models import model_to_dict
from django.conf import settings
from django.db.models.functions import Coalesce
from django.db.models import Q, Value, Max
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.template.loader import render_to_string

from translitua import translitua
import select2.fields
import select2.models
from dateutil.parser import parse as dt_parse
from cacheops import cached

from core.fields import RedactorField
from core.model.base import AbstractNode
from core.model.translations import Ua2EnDictionary
from core.utils import (
    render_date,
    lookup_term,
    parse_fullname,
    translate_into,
    ceil_date,
    localized_fields,
    localized_field,
    get_localized_field,
    translit_from,
    translate_through_dict,
)
from core.model.declarations import Declaration
from core.model.connections import Person2Person, Person2Company, Person2Country

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
        (3, _("Діяч, що виконуює значні функції в міжнародній організації")),
        (4, _("Пов'язана особа")),
        (5, _("Член сім'ї")),
    )

    last_name = models.CharField(_("Прізвище"), max_length=40)
    first_name = models.CharField(_("Ім'я"), max_length=40)
    patronymic = models.CharField(_("По батькові"), max_length=40, blank=True)

    publish = models.BooleanField(_("Опублікувати"), default=False)
    is_pep = models.BooleanField(_("Є PEPом"), default=True)
    imported = models.BooleanField(_("Був імпортований з гугл-таблиці"), default=False)
    
    inn = models.CharField(_("ІНН"), max_length=40, null=True, blank=True)

    photo = models.ImageField(_("Світлина"), blank=True, upload_to="images")
    dob = models.DateField(_("Дата народження"), blank=True, null=True)
    dob_details = models.IntegerField(
        _("Дата народження: точність"),
        choices=((0, _("Точна дата")), (1, _("Рік та місяць")), (2, _("Тільки рік"))),
        default=0,
    )

    city_of_birth = models.CharField(_("Місто народження"), max_length=100, blank=True)

    related_countries = models.ManyToManyField(
        "Country",
        verbose_name=_("Пов'язані країни"),
        through="Person2Country",
        related_name="people",
    )

    reputation_assets = RedactorField(_("Статки"), blank=True)

    reputation_sanctions = RedactorField(_("Наявність санкцій"), blank=True)
    reputation_crimes = RedactorField(_("Кримінальні провадження"), blank=True)
    reputation_manhunt = RedactorField(_("Перебування у розшуку"), blank=True)
    reputation_convictions = RedactorField(_("Наявність судимості"), blank=True)

    related_persons = select2.fields.ManyToManyField(
        "self",
        through="Person2Person",
        symmetrical=False,
        ajax=True,
        search_field=(lambda q: Q(last_name__icontains=q) | Q(first_name__icontains=q)),
    )

    related_companies = models.ManyToManyField("Company", through="Person2Company")

    wiki = RedactorField(_("Вікі-стаття"), blank=True)
    wiki_draft = RedactorField(_("Чернетка вікі-статті"), blank=True)
    names = models.TextField(_("Варіанти написання імені"), blank=True)

    also_known_as = models.TextField(_("Інші імена"), blank=True)

    type_of_official = models.IntegerField(
        _("Тип ПЕП"), choices=_types_of_officials, blank=True, null=True
    )

    risk_category = models.CharField(
        _("Рівень ризику"),
        choices=(
            ("danger", _("Неприйнятно високий")),
            ("high", _("Високий")),
            ("medium", _("Середній")),
            ("low", _("Низький")),
        ),
        max_length=6,
        default="low",
    )

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    hash = models.CharField(_("Хеш"), max_length=40, blank=True)

    reason_of_termination = models.IntegerField(
        _("Причина припинення статусу ПЕП"),
        choices=_reasons_of_termination,
        blank=True,
        null=True,
    )

    termination_date = models.DateField(
        _("Дата припинення статусу ПЕП"),
        blank=True,
        null=True,
        help_text=_(
            "Вказується реальна дата зміни без врахування 3 років (реальна дата звільнення, тощо)"
        ),
    )
    termination_date_details = models.IntegerField(
        _("Дата припинення статусу ПЕП: точність"),
        choices=((0, _("Точна дата")), (1, _("Рік та місяць")), (2, _("Тільки рік"))),
        default=0,
    )

    declarator_id = models.IntegerField(_("ID в системі declarator (RU)"), null=True)

    last_change = models.DateTimeField(
        _("Дата останньої зміни сторінки профіля"), blank=True, null=True
    )

    last_editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_("Автор останньої зміни сторінки профілю"),
        blank=True,
        null=True,
    )

    _last_modified = models.DateTimeField(_("Остання зміна"), null=True, blank=True)
    proofs = GenericRelation("RelationshipProof", verbose_name="Ссылки, социальные сети и документы")

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "last_name__icontains", "first_name__icontains")

    def __unicode__(self):
        return "%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    @property
    def date_of_birth(self):
        return render_date(self.dob, self.dob_details)

    @property
    def termination_date_human(self):
        return render_date(self.termination_date, self.termination_date_details)

    @property
    def terminated(self):
        # (1, _("Помер")),
        # (2, _("Звільнився/склав повноваження")),
        # (3, _("Пов'язана особа або член сім'ї - ПЕП помер")),
        # (4, _("Пов'язана особа або член сім'ї - ПЕП припинив бути ПЕПом")),
        # (5, _("Зміни у законодавстві що визначає статус ПЕПа")),
        # (6, _("Зміни форми власності юр. особи посада в котрій давала статус ПЕПа")),

        if self.reason_of_termination in [1, 3]:
            return True

        if (
            self.reason_of_termination in [2, 4, 5, 6]
            and self.termination_date is not None
        ):
            if (
                ceil_date(self.termination_date, self.termination_date_details)
                + datetime.timedelta(days=3 * 365)
                <= datetime.date.today()
            ):
                return True

        return False

    @property
    def died(self):
        return self.reason_of_termination == 1

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
        base_qs = (
            self.person2company_set.prefetch_related("to_company")
            .exclude(**{localized_field("relationship_type"): "Клієнт банку"})
            .only(
                *(
                    ["to_company__id", "date_finished", "date_finished_details"]
                    + localized_fields(
                        [
                            "to_company__short_name",
                            "to_company__name",
                            "relationship_type",
                        ],
                        langs=settings.LANGUAGE_CODES,
                    )
                )
            )
        )

        qs = base_qs.order_by(
            "-is_employee", "-date_finished", "-date_established"
        ).exclude(
            date_finished__isnull=True, date_established__isnull=True  # AND!
        )

        if qs:
            return qs

        # If nothing is found we are going to return the position that
        # has finished date set to null or the most recent one.
        # In contrast with previous query it'll also return those positions
        # where date_finished and date_established == null.
        qs = base_qs.order_by("-is_employee", "-date_finished")

        return qs

    @property
    def day_of_dismissal(self):
        dday = self._last_workplace().filter(is_employee=True).first()
        if dday:
            return render_date(dday.date_finished, dday.date_finished_details)
        else:
            return False

    def _last_workplace_from_declaration(self):
        return (
            Declaration.objects.filter(person=self, confirmed="a")
            .exclude(doc_type="Кандидата на посаду")
            .order_by("-nacp_declaration", "-year")
            .only(
                *(
                    ["year", "url"]
                    + localized_fields(
                        ["office", "position"], langs=settings.LANGUAGE_CODES
                    )
                )
            )[:1]
        )

    @cached(timeout = 24 * 60 * 60)
    def last_workplace_in_lang(self, lang):
        qs = self._last_workplace()
        if qs:
            l = qs[0]
            return {
                "company": get_localized_field(l.to_company, "short_name", lang)
                or get_localized_field(l.to_company, "name", lang),
                "company_id": l.to_company.pk,
                "position": get_localized_field(l, "relationship_type", lang),
            }
        else:
            qs = self._last_workplace_from_declaration()
            if qs:
                d = qs[0]
                return {
                    "company": get_localized_field(d, "office", lang),
                    "company_id": None,
                    "position": get_localized_field(d, "position", lang),
                }

        return ""

    @property
    # Deprecated
    def last_workplace(self):
        return self.last_workplace_in_lang(settings.LANGUAGE_CODE)

    @property
    # Deprecated
    def last_workplace_en(self):
        return self.last_workplace_in_lang("en")

    # Fuuugly hack
    @property
    def translated_last_workplace(self):
        return self.last_workplace_in_lang(get_language())

    @property
    def workplaces(self):
        # Coalesce works by taking the first non-null value.  So we give it
        # a date far before any non-null values of last_active.  Then it will
        # naturally sort behind instances of Box with a non-null last_active
        # value.
        # djangoproject.com/en/1.8/ref/models/database-functions/#coalesce
        the_past = datetime.datetime.now() - datetime.timedelta(days=30 * 365)

        timeline = (
            self.person2company_set.prefetch_related(
                "to_company", "proofs", "proofs__proof_document"
            )
            .filter(is_employee=True)
            .annotate(
                fixed_date_established=Coalesce("date_established", Value(the_past))
            )
            .order_by("-fixed_date_established")
        )

        return timeline

    @property
    def assets(self):
        return self.person2company_set.prefetch_related(
            "to_company", "proofs", "proofs__proof_document"
        ).filter(
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
            ),
        )

    @property
    def all_related_companies(self):
        the_past = datetime.datetime.now() - datetime.timedelta(days=30 * 365)

        companies = self.person2company_set.prefetch_related(
            "to_company", "proofs", "proofs__proof_document"
        ).filter(is_employee=False).annotate(
            fixed_date_established=Coalesce("date_established", Value(the_past))
        ).order_by("-fixed_date_established")

        banks = []
        rest = []
        for c in companies:
            if get_localized_field(c, "relationship_type") == "Клієнт банку":
                banks.append(c)
            else:
                rest.append(c)

        return {"banks": banks, "rest": rest}

    @property
    def all_related_persons(self):
        related_persons = [
            (
                i.to_relationship_type,
                i.from_relationship_type,
                deepcopy(i.to_person),
                i
            )
            for i in self.to_persons.prefetch_related(
                "to_person", "proofs", "proofs__proof_document"
            ).defer(
                "to_person__reputation_assets",
                "to_person__reputation_sanctions",
                "to_person__reputation_crimes",
                "to_person__reputation_manhunt",
                "to_person__reputation_convictions",
                "to_person__wiki",
                "to_person__names",
                "to_person__hash",
            )
        ] + [
            (
                i.from_relationship_type,
                i.to_relationship_type,
                deepcopy(i.from_person),
                i,
            )
            for i in self.from_persons.prefetch_related(
                "from_person", "proofs", "proofs__proof_document"
            ).defer(
                "from_person__reputation_assets",
                "from_person__reputation_sanctions",
                "from_person__reputation_crimes",
                "from_person__reputation_manhunt",
                "from_person__reputation_convictions",
                "from_person__wiki",
                "from_person__names",
                "from_person__hash",
            )
        ]

        res = {"family": [], "personal": [], "business": [], "all": []}

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

    def localized_full_name(self, lang):
        return (
            "%s %s %s"
            % (
                getattr(self, localized_field("first_name", lang)),
                getattr(self, localized_field("patronymic", lang)),
                getattr(self, localized_field("last_name", lang)),
            )
        ).replace("  ", " ")

    def localized_shortname(self, lang):
        return (
            "%s %s"
            % (
                getattr(self, localized_field("first_name", lang)),
                getattr(self, localized_field("last_name", lang)),
            )
        ).replace("  ", " ")

    @property
    def full_name(self):
        return self.localized_full_name(get_language())

    @property
    def full_name_en(self):
        return self.localized_full_name("en")

    def to_dict(self):
        """
        Convert Person model to an indexable presentation for ES.
        """
        d = model_to_dict(
            self,
            fields=["id", "dob", "dob_details", "is_pep", "names", "last_change"]
            + localized_fields(
                [
                    "last_name",
                    "first_name",
                    "patronymic",
                    "wiki",
                    "city_of_birth",
                    "reputation_sanctions",
                    "reputation_convictions",
                    "reputation_assets",
                    "reputation_crimes",
                    "reputation_manhunt",
                    "also_known_as",
                ],
                settings.LANGUAGE_CODES,
            ),
        )

        d["related_persons"] = [
            i.to_dict() for i in self.to_persons.prefetch_related("to_person")
        ] + [
            i.to_dict_reverse()
            for i in self.from_persons.prefetch_related("from_person")
        ]
        d["related_countries"] = [
            i.to_dict() for i in self.person2country_set.prefetch_related("to_country")
        ]
        d["related_companies"] = [
            i.to_company_dict()
            for i in self.person2company_set.prefetch_related("to_company")
        ]

        d["declarations"] = [
            i.to_dict() for i in Declaration.objects.filter(person=self, confirmed="a")
        ]

        manhunt_records = self.manhunt_records
        if manhunt_records:
            curr_lang = get_language()

            activate("uk")
            d["reputation_manhunt_uk"] = render_to_string(
                "_manhunt_records_uk.jinja", {"manhunt_records": manhunt_records}
            ) + (d["reputation_manhunt_uk"] or "")

            activate("en")
            d["reputation_manhunt_en"] = render_to_string(
                "_manhunt_records_en.jinja", {"manhunt_records": manhunt_records}
            ) + (d["reputation_manhunt_en"] or "")
            activate(curr_lang)

        d["photo"] = settings.SITE_URL + self.photo.url if self.photo else ""
        d["photo_path"] = self.photo.name if self.photo else ""
        d["date_of_birth"] = self.date_of_birth
        d["terminated"] = self.terminated
        d["last_modified"] = self.last_modified
        d["died"] = self.died
        if d["terminated"]:
            for lang in settings.LANGUAGE_CODES:
                d[localized_field("reason_of_termination", lang)] = translate_into(
                    self.get_reason_of_termination_display(), lang
                )

            d["termination_date_human"] = self.termination_date_human

        last_workplace = self.last_workplace
        if last_workplace:
            d["last_workplace"] = last_workplace["company"]
            d["last_job_title"] = last_workplace["position"]
            d["last_job_id"] = last_workplace["company_id"]

            for lang in settings.LANGUAGE_CODES:
                last_workplace_translated = self.last_workplace_in_lang(lang)
                d[localized_field("last_workplace", lang)] = last_workplace_translated[
                    "company"
                ]
                d[localized_field("last_job_title", lang)] = last_workplace_translated[
                    "position"
                ]

        for lang in settings.LANGUAGE_CODES:
            d[localized_field("type_of_official", lang)] = translate_into(
                self.get_type_of_official_display(), lang
            )

            d[localized_field("full_name", lang)] = self.localized_full_name(lang)

        def generate_suggestions(last_name, first_name, patronymic, *args):
            if not last_name:
                return []

            return [
                {"input": " ".join(filter(None, [last_name, first_name, patronymic])), "weight": 5},
                {"input": " ".join(filter(None, [first_name, patronymic, last_name])), "weight": 2},
                {"input": " ".join(filter(None, [first_name, last_name])), "weight": 2},
            ]

        input_variants = [
            generate_suggestions(
                d[localized_field("last_name")],
                d[localized_field("first_name")],
                d[localized_field("patronymic")],
            )
        ]

        input_variants += list(
            map(lambda x: generate_suggestions(*parse_fullname(x)), self.parsed_names)
        )

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

    @property
    def foreign_citizenship_or_registration(self):
        return self.person2country_set.prefetch_related("to_country").filter(
            relationship_type__in=["citizenship", "registered_in"]
        )

    @property
    def foreign_citizenship(self):
        return self.person2country_set.prefetch_related("to_country").filter(
            relationship_type="citizenship"
        )

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    def save(self, *args, **kwargs):
        for lang in settings.LANGUAGE_CODES:
            if lang == settings.LANGUAGE_CODE:
                continue

            for field in ["first_name", "last_name", "patronymic", "also_known_as"]:
                val = get_localized_field(self, field, settings.LANGUAGE_CODE)
                setattr(
                    self,
                    localized_field(field, lang),
                    translit_from(val or "", settings.LANGUAGE_CODE),
                )

            cob_term = get_localized_field(
                self, "city_of_birth", settings.LANGUAGE_CODE
            )
            cob_trans = get_localized_field(self, "city_of_birth", lang)
            if cob_term and (cob_term == cob_trans or not cob_trans):
                val = translate_through_dict(
                    cob_term,
                    settings.LANGUAGE_CODE,
                    lang,
                )

                if val is not None:
                    setattr(self, localized_field("city_of_birth", lang), val)
                else:
                    setattr(
                        self,
                        localized_field("city_of_birth", lang),
                        ""
                    )

        super(Person, self).save(*args, **kwargs)

    def get_declarations(self):
        decls = Declaration.objects.filter(person=self, confirmed="a").order_by(
            "-year", "-nacp_declaration"
        )

        corrected = []
        res = []
        # Filtering out original declarations, if there are
        # also corrected one
        for d in decls:
            if not d.nacp_declaration:
                continue

            if d.source["intro"].get("corrected"):
                corrected.append((d.year, d.source["intro"].get("doc_type")))

        for d in decls:
            if d.nacp_declaration and not d.source["intro"].get("corrected"):
                if (d.year, d.source["intro"].get("doc_type")) in corrected:
                    continue

            res.append(d)

        return res

    def get_node(self):
        res = super(Person, self).get_node()

        node = {
            "name": self.localized_shortname(get_language()),
            "full_name": self.localized_full_name(get_language()),
            "is_pep": self.is_pep,
            "kind": unicode(ugettext_lazy(self.get_type_of_official_display() or ""))
        }
        last_workplace = self.translated_last_workplace

        if last_workplace:
            node["description"] = "{position} @ {company}".format(**last_workplace)

        res["data"].update(node)

        return res

    def get_node_info(self, with_connections=False):
        this_node = self.get_node()
        nodes = [this_node]
        edges = []
        all_connected = set()

        # Because of a complicated logic here we are piggybacking on
        # existing method that handles both directions of relations
        for p in self.all_related_persons["all"]:
            child_node_id = p.get_node_id()

            if with_connections:
                child_node = p.get_node_info(False)

                nodes += child_node["nodes"]
                edges += child_node["edges"]

                edges.append(
                    {
                        "data": {
                            "relation": unicode(ugettext_lazy(p.rtype)),
                            "model": p.connection._meta.model_name,
                            "pk": p.connection.pk,
                            "id": "{}-{}".format(
                                p.connection._meta.model_name, p.connection.pk
                            ),
                            "share": 0,
                            "source": this_node["data"]["id"],
                            "target": child_node_id,
                            "is_latest": True
                        }
                    }
                )

            all_connected.add(child_node_id)

        companies = self.person2company_set.prefetch_related("to_company")

        worked_for = {}
        connected_to = {}

        if with_connections:
            for c in companies:
                c.is_latest = False

                child_node_id = c.to_company.get_node_id()

                if c.is_employee:
                    bucket = worked_for
                else:
                    bucket = connected_to

                if child_node_id not in bucket:
                    bucket[child_node_id] = c
                else:
                    compare_with = bucket[child_node_id]

                    # When comparing two connections
                    if c.date_finished is not None or c.date_established is not None:
                        # Candidate with date_finished and date_established not set looses
                        if compare_with.date_finished is None and compare_with.date_established is None:
                            bucket[child_node_id] = c
                        else:
                            dt_now = (datetime.datetime.now() + datetime.timedelta(days=7)).date()

                            a_date_established = compare_with.date_established or dt_now
                            b_date_established = c.date_established or dt_now

                            a_date_finished = compare_with.date_finished or dt_now
                            b_date_finished = c.date_finished or dt_now

                            # Candidate with later date finished or open date_finished wins
                            if b_date_finished > a_date_finished:
                                bucket[child_node_id] = c
                            elif b_date_finished == a_date_finished:
                                # if both date finished are the same (for example two connections has open end)
                                # those with latest date_established wins
                                if b_date_established > a_date_established:
                                    bucket[child_node_id] = c


            for bucket in [worked_for, connected_to]:
                for c in bucket.values():
                    c.is_latest = True

        for c in companies:
            child_node_id = c.to_company.get_node_id()

            if with_connections:
                child_node = c.to_company.get_node_info(False)
                nodes += child_node["nodes"]
                edges += child_node["edges"]

                edges.append(
                    {
                        "data": {
                            "relation": unicode(c.relationship_type),
                            "model": c._meta.model_name,
                            "pk": c.pk,
                            "id": "{}-{}".format(
                                c._meta.model_name, c.pk
                            ),
                            "source": this_node["data"]["id"],
                            "share": float(c.share or 0),
                            "target": child_node_id,
                            "is_latest": c.is_latest
                        }
                    }
                )

            all_connected.add(child_node_id)

        this_node["data"]["all_connected"] = list(all_connected)
        return {"edges": edges, "nodes": nodes}

    @property
    def manhunt_records(self):
        return [
            {
                "last_updated_from_dataset": rec.last_updated_from_dataset,
                "lost_date": dt_parse(rec.matched_json["LOST_DATE"], yearfirst=True),
                "articles_uk": rec.matched_json["ARTICLE_CRIM"],
                "articles_en": rec.matched_json["ARTICLE_CRIM"]
                .lower()
                .replace("ст.", "article ")
                .replace("ч.", "pt. "),
            }
            for rec in self.adhoc_matches.filter(status="a", dataset_id="wanted_ia")
        ]

    @property
    def last_modified(self):
        p2p_conn = Person2Person.objects.filter(
            Q(from_person=self) | Q(to_person=self)
        ).aggregate(mm=Max("_last_modified"))["mm"]

        p2comp_conn = Person2Company.objects.filter(Q(from_person=self)).aggregate(
            mm=Max("_last_modified")
        )["mm"]

        p2cont_conn = Person2Country.objects.filter(Q(from_person=self)).aggregate(
            mm=Max("_last_modified")
        )["mm"]

        seq = list(
            filter(
                None,
                [
                    p2p_conn,
                    p2comp_conn,
                    p2cont_conn,
                    self.last_change,
                    self._last_modified,
                ],
            )
        )
        if seq:
            return max(seq)

    @property
    def external_links(self):
        social_networks = {
            "facebook.com": "Facebook",
            "twitter.com": "Twitter",
            "vk.com": "Vkontakte",
            "instagram.com": "Instagram",
            "ok.ru": "Odnoklassniki",
            "linkedin.com": "LinkedIn"
        }
        other_networks = {
            "ru.wikipedia.org": "Wikipedia",
            "en.wikipedia.org": "Wikipedia",
            "de.wikipedia.org": "Wikipedia",
            "uk.wikipedia.org": "Wikipedia",
        }

        res = {
            "social_networks": [],
            "other": []
        }

        for proof in self.proofs.all():
            if proof.proof:
                domain = urlparse(proof.proof).hostname.replace("www.", "").lower()

                if domain in social_networks:
                    res["social_networks"].append({
                        "type": social_networks[domain],
                        "title": social_networks[domain],
                        "url": proof.proof
                    })
                else:
                    res["other"].append({
                        "type": domain,
                        "title": proof.proof_title or other_networks.get(domain, domain),
                        "url": proof.proof
                    })

        return res

    class Meta:
        verbose_name = _("Фізична особа")
        verbose_name_plural = _("Фізичні особи")

        index_together = [["last_name", "first_name"]]

        permissions = (
            ("export_persons", "Can export the dataset"),
            (
                "export_id_and_last_modified",
                "Can export the dataset with person id and date of last modification",
            ),
        )
