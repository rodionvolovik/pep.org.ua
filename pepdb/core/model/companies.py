# coding: utf-8
from __future__ import unicode_literals
import re
from copy import copy, deepcopy
from collections import defaultdict

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_lazy, activate, get_language
from django.forms.models import model_to_dict
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist

from core.fields import RedactorField

from core.model.base import AbstractNode
from core.model.translations import Ua2EnDictionary
from core.utils import (
    render_date,
    lookup_term,
    translate_into,
    localized_fields,
    localized_field,
    get_localized_field,
    translate_through_dict,
)
from core.model.connections import Company2Company, Company2Country, Person2Company


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
        9: _("в процесі реорганізації"), 
        10: _("в процесі реорганізації у формі виділення")
    }

    name = models.CharField(_("Повна назва"), max_length=512)
    short_name = models.CharField(_("Скорочена назва"), max_length=200, blank=True)

    also_known_as = models.TextField(_("Назви іншими мовами або варіації"), blank=True)

    publish = models.BooleanField(_("Опублікувати"), default=False)
    founded = models.DateField(_("Дата створення"), blank=True, null=True)
    founded_details = models.IntegerField(
        _("Дата створення: точність"),
        choices=((0, _("Точна дата")), (1, _("Рік та місяць")), (2, _("Тільки рік"))),
        default=0,
    )

    status = models.IntegerField(
        _("Поточний стан"), choices=_status_choices.items(), default=0
    )
    closed_on = models.DateField(_("Дата припинення"), blank=True, null=True)
    closed_on_details = models.IntegerField(
        _("Дата припинення: точність"),
        choices=((0, _("Точна дата")), (1, _("Рік та місяць")), (2, _("Тільки рік"))),
        default=0,
    )

    @property
    def founded_human(self):
        return render_date(self.founded, self.founded_details)

    state_company = models.BooleanField(_("Керівник — ПЕП"), default=False)

    legal_entity = models.BooleanField(_("Юрособа"), default=True)

    edrpou = models.CharField(_("ЄДРПОУ"), max_length=50, blank=True)
    ogrn_code = models.CharField(_("ОГРН"), max_length=50, blank=True, null=True)
    website = models.URLField(_("Вебсайт"), max_length=255, blank=True, null=True)

    zip_code = models.CharField(_("Індекс"), max_length=20, blank=True)
    city = models.CharField(_("Місто"), max_length=255, blank=True)
    street = models.CharField(_("Вулиця"), max_length=100, blank=True)
    appt = models.CharField(_("№ будинку, офісу"), max_length=50, blank=True)
    raw_address = models.TextField(_('"Сира" адреса'), blank=True)

    wiki = RedactorField(_("Вікі-стаття"), blank=True)

    other_founders = RedactorField(
        _("Інші засновники"), help_text=_("Через кому, не PEP"), blank=True
    )

    other_recipient = models.CharField(
        _("Бенефіціарій"), help_text=_("Якщо не є PEPом"), blank=True, max_length=200
    )

    other_owners = RedactorField(
        _("Інші власники"), help_text=_("Через кому, не PEP"), blank=True
    )

    other_managers = RedactorField(
        _("Інші керуючі"), help_text=_("Через кому, не PEP"), blank=True
    )

    bank_name = RedactorField(_("Фінансова інформація"), blank=True)

    sanctions = RedactorField(_("Санкції"), blank=True)

    related_companies = models.ManyToManyField(
        "self", through="Company2Company", symmetrical=False
    )

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

    works_for_peps = models.BooleanField(_("Обслуговує PEPів"), default=False)
    subject_of_monitoring = models.BooleanField(
        _("Суб'єкт фінансового моніторингу"), default=False
    )
    _last_modified = models.DateTimeField(_("Остання зміна"), null=True, blank=True)
    proofs = GenericRelation("RelationshipProof")

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "short_name__icontains", "name__icontains")

    def __unicode__(self):
        return self.short_name or self.name

    def to_dict(self):
        d = model_to_dict(
            self,
            fields=[
                "id",
                "state_company",
                "edrpou",
                "ogrn_code",
                "wiki",
                "city",
                "street",
                "other_founders",
                "other_recipient",
                "other_owners",
                "other_managers",
                "bank_name",
                "also_known_as",
            ]
            + localized_fields(["name", "short_name"], settings.LANGUAGE_CODES),
        )

        d["related_persons"] = [
            i.to_person_dict()
            for i in self.from_persons.prefetch_related("from_person")
        ]

        d["related_countries"] = [
            i.to_dict() for i in self.from_countries.prefetch_related("to_country")
        ]

        d["related_companies"] = [
            i.to_dict() for i in self.to_companies.prefetch_related("to_company")
        ] + [
            i.to_dict_reverse()
            for i in self.from_companies.prefetch_related("from_company")
        ]

        d["status"] = self.get_status_display()
        for lang in settings.LANGUAGE_CODES:
            d[localized_field("status", lang)] = translate_into(
                self.get_status_display(), lang
            )

        d["founded"] = self.founded_human
        d["closed"] = self.closed_on_human
        d["last_modified"] = self.last_modified

        suggestions = []

        for field in localized_fields(["name", "short_name"], settings.LANGUAGE_CODES):
            if not field:
                continue

            chunks = list(map(lambda x: x.strip("'\",.-“”«»"), field.split(" ")))

            for i in xrange(len(chunks)):
                variant = copy(chunks)
                variant = [variant[i]] + variant[:i] + variant[i + 1 :]
                suggestions.append(" ".join(variant))

        if self.edrpou:
            edrpou_chunks = list(
                filter(
                    None,
                    map(
                        unicode.strip,
                        re.split("([a-z]+)", self.edrpou, flags=re.IGNORECASE),
                    ),
                )
            )

            suggestions += edrpou_chunks
            suggestions.append(self.edrpou.lstrip("0"))

            if self.edrpou.isdigit():
                suggestions.append(self.edrpou.rjust(8, "0"))

            d["code_chunks"] = edrpou_chunks

        d["name_suggest"] = [{"input": x} for x in set(suggestions)]

        for lang in settings.LANGUAGE_CODES:
            d[localized_field("name_suggest_output")] = (
                d[localized_field("short_name")] or d[localized_field("name")]
            )

        d["_id"] = d["id"]

        return d

    def save(self, *args, **kwargs):
        for lang in settings.LANGUAGE_CODES:
            if lang == settings.LANGUAGE_CODE:
                continue

            for field in ["name", "short_name"]:
                if not get_localized_field(self, field, lang) or get_localized_field(
                    self, field, lang
                ) == get_localized_field(self, field):
                    val = translate_through_dict(
                        get_localized_field(self, field), settings.LANGUAGE_CODE, lang
                    )

                    if val is not None:
                        setattr(self, localized_field(field, lang), val)
                    else:
                        setattr(
                            self,
                            localized_field(field, lang),
                            get_localized_field(self, field),
                        )

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

    # Deprecated
    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    @property
    def all_related_persons(self):
        related_persons = [
            (get_localized_field(i, "relationship_type"), deepcopy(i.from_person), i)
            for i in self.from_persons.prefetch_related("from_person")
            .defer(
                "from_person__reputation_assets",
                "from_person__reputation_crimes",
                "from_person__reputation_manhunt",
                "from_person__reputation_convictions",
                "from_person__wiki",
                "from_person__names",
                "from_person__hash",
            )
            .order_by(
                *localized_fields(["from_person__last_name", "from_person__first_name"])
            )
        ]

        res = {
            "managers": [],
            "founders": [],
            "sanctions": [],
            "bank_customers": [],
            "rest": [],
        }

        for rtp, p, rel in related_persons:
            p.rtype = rtp
            p.connection = rel

            if rtp.lower() in [
                _("руководитель"),
                _("заместитель руководителя"),
                _("глава"),
                _("директор"),
                _("генеральный директор"),
                _("исполнительный директор"),
                _("председатель совета директоров"),
                _("председатель совета"),
                _("председатель правления"),
                _("председатель"),
                _("секретарь"),
                _("член совета"),
                _("член совета директоров"),
                _("член правления"),
                _("управляющий"),
                _("глава администрации"),
                _("главный врач"),
                _("глава совета"),
                _("главный редактор"),
                _("ректор"),
                _("мэр"),
                _("президент"),
                _("советник председателя"),
                _("сопредседатель"),
                _("начальник"),
            ]:
                res["managers"].append(p)

            elif rtp.lower() in [
                _("засновники"),
                _("засновник/учасник"),
                _("колишній засновник/учасник"),
            ]:
                res["founders"].append(p)

            elif rtp.lower() in [_("клієнт банку")]:
                res["bank_customers"].append(p)

            if p.reputation_sanctions:
                res["sanctions"].append(p)


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
            relationship_type="registered_in"
        )

    @property
    def all_related_companies(self):
        related_companies = [
            (i.relationship_type, deepcopy(i.to_company), i, True)
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
            (i.reverse_relationship_type, deepcopy(i.from_company), i, False)
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

        res = {"founders": [], "rest": [], "banks": [], "all": []}

        for rtp, p, rel, direction in sorted(
            related_companies, key=lambda x: get_localized_field(x[1], "name")
        ):
            p.rtype = rtp
            p.direction = direction
            p.connection = rel

            if rtp in [
                "Засновник",
                "Співзасновник",
                "Колишній власник/засновник",
                "Колишній співвласник/співзасновник",
            ]:
                res["founders"].append(p)
            elif rtp == "Клієнт банку":
                res["banks"].append(p)
            else:
                res["rest"].append(p)

            res["all"].append(p)

        return res


    def get_node(self):
        res = super(Company, self).get_node()

        node = {
            "name": self.short_name or self.name,
            "full_name": self.name,
            "description": self.edrpou,
            "state_company": self.state_company,
            "is_closed": bool(self.closed_on_human),
            "kind": unicode(
                ugettext_lazy("Державна компанія чи установа")
                if self.state_company
                else ugettext_lazy("Приватна компанія")
            ),
        }

        res["data"].update(node)

        return res


    def get_node_info(self, with_connections=False):
        this_node = self.get_node()
        nodes = [this_node]
        edges = []
        all_connected = set()

        # Because of a complicated logic here we are piggybacking on
        # existing method that handles both directions of relations
        for p in self.all_related_persons["rest"]:
            if p.rtype.lower() in [_("клієнт банку")]:
                continue                    

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
                            "target": this_node["data"]["id"],
                            "source": child_node_id,
                            "is_latest": True,
                        }
                    }
                )

            all_connected.add(child_node_id)

        for c in self.all_related_companies["all"]:
            child_node_id = c.get_node_id()

            if with_connections:
                child_node = c.get_node_info(False)
                nodes += child_node["nodes"]
                edges += child_node["edges"]
                if c.direction:
                    source = child_node_id
                    target = this_node["data"]["id"]
                else:
                    source = this_node["data"]["id"]
                    target = child_node_id

                edges.append(
                    {
                        "data": {
                            "relation": unicode(c.connection.relationship_type),
                            "model": c.connection._meta.model_name,
                            "pk": c.connection.pk,
                            "id": "{}-{}".format(
                                c.connection._meta.model_name, c.connection.pk
                            ),
                            "source": source,
                            "share": float(c.connection.equity_part or 0),
                            "target": target,
                            "is_latest": True,
                        }
                    }
                )

            all_connected.add(child_node_id)

        this_node["data"]["all_connected"] = list(all_connected)
        return {"edges": edges, "nodes": nodes}

    @property
    def closed_on_human(self):
        return render_date(self.closed_on, self.closed_on_details)

    @property
    def last_modified(self):
        c2c_conn = Company2Company.objects.filter(
            Q(from_company=self) | Q(to_company=self)
        ).aggregate(mm=Max("_last_modified"))["mm"]

        c2p_conn = Person2Company.objects.filter(to_company=self).aggregate(
            mm=Max("_last_modified")
        )["mm"]

        c2cont_conn = Company2Country.objects.filter(from_company=self).aggregate(
            mm=Max("_last_modified")
        )["mm"]

        seq = list(
            filter(
                None,
                [
                    c2c_conn,
                    c2p_conn,
                    c2cont_conn,
                    self.last_change,
                    self._last_modified,
                ],
            )
        )
        if seq:
            return max(seq)

    objects = CompanyManager()

    class Meta:
        verbose_name = _("Юридична особа")
        verbose_name_plural = _("Юридичні особи")

        permissions = (("export_companies", "Can export the dataset of companies"),)
