# coding: utf-8
from __future__ import unicode_literals
from collections import OrderedDict


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop as __
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


from core.fields import RedactorField
from core.utils import lookup_term, translate_into, localized_fields, localized_field, get_localized_field, translate_through_dict
from core.model.base import AbstractRelationship
from core.model.translations import Ua2EnDictionary


class Person2Person(AbstractRelationship):
    _relationships_explained = OrderedDict(
        [
            (__("чоловік"), [__("дружина")]),
            (__("дружина"), [__("чоловік")]),
            (__("чоловік/дружина"), [__("чоловік/дружина")]),
            (__("батько"), [__("син"), __("дочка"), __("син/дочка")]),
            (__("мати"), [__("син"), __("дочка"), __("син/дочка")]),
            (__("батько/мати"), [__("син"), __("дочка"), __("син/дочка")]),
            (__("син"), [__("батько"), __("мати"), __("батько/мати")]),
            (__("дочка"), [__("батько"), __("мати"), __("батько/мати")]),
            (__("син/дочка"), [__("батько"), __("мати"), __("батько/мати")]),
            (__("вітчим"), [__("пасинок"), __("падчерка")]),
            (__("мачуха"), [__("пасинок"), __("падчерка")]),
            (__("пасинок"), [__("вітчим"), __("мачуха")]),
            (__("падчерка"), [__("вітчим"), __("мачуха")]),
            (__("рідний брат"), [__("рідна сестра"), __("рідний брат")]),
            (__("рідна сестра"), [__("рідна сестра"), __("рідний брат")]),
            (__("дід"), [__("внук"), __("внучка")]),
            (__("баба"), [__("внук"), __("внучка")]),
            (__("прадід"), [__("правнук"), __("правнучка")]),
            (__("прабаба"), [__("правнук"), __("правнучка")]),
            (__("внук"), [__("дід"), __("баба")]),
            (__("внучка"), [__("дід"), __("баба")]),
            (__("правнук"), [__("прадід"), __("прабаба")]),
            (__("правнучка"), [__("прадід"), __("прабаба")]),
            (__("зять"), [__("теща"), __("тесть")]),
            (__("невістка"), [__("свекор"), __("свекруха")]),
            (__("тесть"), [__("зять")]),
            (__("теща"), [__("зять")]),
            (__("свекор"), [__("невістка")]),
            (__("свекруха"), [__("невістка")]),
            (__("усиновлювач"), [__("усиновлений")]),
            (__("усиновлений"), [__("усиновлювач")]),
            (
                __("опікун чи піклувальник"),
                [__("особа, яка перебуває під опікою або піклуванням")],
            ),
            (
                __("особа, яка перебуває під опікою або піклуванням"),
                [__("опікун чи піклувальник")],
            ),
            (
                __("особи, які спільно проживають"),
                [__("особи, які спільно проживають")],
            ),
            (
                __("пов'язані спільним побутом і мають взаємні права та обов'язки"),
                [__("пов'язані спільним побутом і мають взаємні права та обов'язки")],
            ),
            (__("ділові зв'язки"), [__("ділові зв'язки")]),
            (__("особисті зв'язки"), [__("особисті зв'язки")]),
        ]
    )

    from_person = models.ForeignKey(
        "Person", verbose_name=_("Персона 1"), related_name="to_persons"
    )
    to_person = models.ForeignKey(
        "Person", verbose_name=_("Персона 2"), related_name="from_persons"
    )

    from_relationship_type = models.CharField(
        _("Персона 1 є"),
        choices=(
            zip(
                _relationships_explained.keys(), map(_, _relationships_explained.keys())
            )
        ),
        max_length=100,
        blank=True,
    )

    to_relationship_type = models.CharField(
        _("Персона 2 є"),
        choices=(
            zip(
                _relationships_explained.keys(), map(_, _relationships_explained.keys())
            )
        ),
        max_length=100,
        blank=True,
    )

    relationship_details = RedactorField(_("Детальний опис зв'язку"), blank=True)

    declarations = ArrayField(
        models.IntegerField(),
        verbose_name=_("Декларації, що підтверджують зв'язок"),
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return "%s (%s) -> %s (%s)" % (
            self.from_person,
            self.get_from_relationship_type_display(),
            self.to_person,
            self.get_to_relationship_type_display(),
        )

    def to_dict(self):
        """
        Convert link between two persons into indexable presentation.
        """
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "is_pep": self.to_person.is_pep,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("relationship_type", lang)] = translate_into(
                self.to_relationship_type, lang
            )
            res[localized_field("person", lang)] = self.to_person.localized_full_name(
                lang
            )

        return res

    def to_dict_reverse(self):
        """
        Convert back link between two persons to indexable presentation.
        """
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "is_pep": self.from_person.is_pep,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("relationship_type", lang)] = translate_into(
                self.from_relationship_type, lang
            )
            res[localized_field("person", lang)] = self.from_person.localized_full_name(
                lang
            )

        return res

    class Meta:
        verbose_name = _("Зв'язок з іншою персоною")
        verbose_name_plural = _("Зв'язки з іншими персонами")


class Person2Company(AbstractRelationship):
    _relationships_explained = [
        __("Президент"),
        __("Прем’єр-міністр"),
        __("Міністр"),
        __("Перший заступник міністра"),
        __("Заступник міністра"),
        __("Керівник"),
        __("Перший заступник керівника"),
        __("Заступник керівника"),
        __("Народний депутат"),
        __("Голова"),
        __("Заступник Голови"),
        __("Перший заступник Голови"),
        __("Член Правління"),
        __("Член Ради"),
        __("Суддя"),
        __("Член"),
        __("Генеральний прокурор"),
        __("Заступник Генерального прокурора"),
        __("Надзвичайний і повноважний посол"),
        __("Головнокомандувач"),
        __("Службовець першої категорії посад"),
        __("Член центрального статутного органу"),
        __("Повірений у справах"),
        __("Засновник/учасник"),
        __("Колишній засновник/учасник"),
        __("Бенефіціарний власник"),
        __("Номінальний власник"),
        __("Номінальний директор"),
        __("Фінансові зв'язки"),
        __("Секретар"),
        __("Керуючий"),
        __("Контролер"),
        __("Клієнт"),
        __("Клієнт банку"),
    ]

    from_person = models.ForeignKey("Person")
    to_company = models.ForeignKey(
        "Company", verbose_name=_("Компанія або установа"), related_name="from_persons"
    )

    relationship_type = models.TextField(_("Тип зв'язку"), blank=True)

    is_employee = models.BooleanField(_("Працює(-вав)"), default=False)

    created_from_edr = models.NullBooleanField(
        _("Запис створено з інформації ЄДР"), default=False
    )

    declarations = ArrayField(
        models.IntegerField(),
        verbose_name=_("Декларації, що підтверджують зв'язок"),
        null=True,
        blank=True,
    )

    share = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=6,
        max_digits=9,
        verbose_name=_("Розмір частки (відсотки)"),
    )

    def __unicode__(self):
        return "%s (%s)" % (self.to_company, self.relationship_type)

    def to_company_dict(self):
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "to_company_is_state": self.to_company.state_company,
            "to_company_edrpou": self.to_company.edrpou,
            "to_company_founded": self.to_company.founded_human,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("relationship_type", lang)] = getattr(
                self, localized_field("relationship_type", lang)
            )
            res[localized_field("to_company", lang)] = getattr(
                self.to_company, localized_field("name", lang)
            )
            res[localized_field("to_company_short", lang)] = getattr(
                self.to_company, localized_field("short_name", lang)
            )

        return res

    def to_person_dict(self):
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "is_pep": self.from_person.is_pep,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("relationship_type", lang)] = getattr(
                self, localized_field("relationship_type", lang)
            )
            res[localized_field("person", lang)] = self.from_person.localized_full_name(
                lang
            )

        return res

    def save(self, *args, **kwargs):
        for lang in settings.LANGUAGE_CODES:
            if lang == settings.LANGUAGE_CODE:
                continue

            if get_localized_field(
                self, "relationship_type", settings.LANGUAGE_CODE
            ) and not get_localized_field(self, "relationship_type", lang):
                val = translate_through_dict(
                    get_localized_field(self, "relationship_type", lang),
                    settings.LANGUAGE_CODE,
                    lang,
                )

                if val is not None:
                    setattr(self, localized_field("relationship_type", lang), val)
                else:
                    setattr(
                        self,
                        localized_field("relationship_type", lang),
                        get_localized_field(
                            self, "relationship_type", settings.LANGUAGE_CODE
                        ),
                    )

        super(Person2Company, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Зв'язок з компанією/установою")
        verbose_name_plural = _("Зв'язки з компаніями/установами")


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
        _("Клієнт банку"),
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
        _("Самостійний структурний підрозділ"),
        _("Головне підприємство"),
        _("Секретар"),
        _("Директор"),
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
        _("Клієнт банку"): _("Банк"),
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
        _("Член наглядового органу)"): _("Підконтрольна"),
        _("Самостійний структурний підрозділ"): _("Головне підприємство"),
        _("Головне підприємство"): _("Самостійний структурний підрозділ"),
        _("Секретар"): _("Клієнт"),
        _("Директор"): _("Клієнт"),
    }

    from_company = models.ForeignKey("Company", related_name="to_companies")
    to_company = models.ForeignKey("Company", related_name="from_companies")

    relationship_type = models.CharField(
        _("Тип зв'язку"),
        choices=zip(_relationships_explained, map(_, _relationships_explained)),
        max_length=50,
        blank=True,
    )

    equity_part = models.FloatField(
        "Частка власності (відсотки)", blank=True, null=True
    )

    @property
    def reverse_relationship_type(self):
        return self._relationships_mapping.get(self.relationship_type)

    def to_dict(self):
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "state_company": self.to_company.state_company,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("company", lang)] = getattr(
                self.to_company, localized_field("name", lang)
            )
            res[localized_field("relationship_type", lang)] = translate_into(
                self.relationship_type, lang
            )

        return res

    def to_dict_reverse(self):
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            "state_company": self.from_company.state_company,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("company", lang)] = getattr(
                self.from_company, localized_field("name", lang)
            )
            res[localized_field("relationship_type", lang)] = translate_into(
                self.relationship_type, lang
            )

        return res

    class Meta:
        verbose_name = _("Зв'язок з компанією")
        verbose_name_plural = _("Зв'язки з компаніями")


class Person2Country(AbstractRelationship):
    from_person = models.ForeignKey("Person", verbose_name=_("Персона"))
    to_country = models.ForeignKey("Country", verbose_name=_("Країна"))

    relationship_type = models.CharField(
        _("Тип зв'язку"),
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
        blank=False,
    )

    def __unicode__(self):
        return "%s у %s" % (self.get_relationship_type_display(), self.to_country)

    def to_dict(self):
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            # TODO
            "relationship_type": self.relationship_type,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("to_country", lang)] = getattr(
                self.to_country, localized_field("name", lang)
            )

        return res

    class Meta:
        verbose_name = _("Зв'язок з країною")
        verbose_name_plural = _("Зв'язки з країнами")


class Company2Country(AbstractRelationship):
    from_company = models.ForeignKey(
        "Company", verbose_name=_("Компанія"), related_name="from_countries"
    )
    to_country = models.ForeignKey("Country", verbose_name=_("Країна"))

    relationship_type = models.CharField(
        _("Тип зв'язку"),
        choices=(
            ("registered_in", _("Зареєстрована")),
            ("under_sanctions", _("Під санкціями")),
        ),
        max_length=30,
        blank=False,
    )

    def to_dict(self):
        res = {
            "date_established": self.date_established_human,
            "date_finished": self.date_finished_human,
            "date_confirmed": self.date_confirmed_human,
            # TODO
            "relationship_type": self.relationship_type,
        }

        for lang in settings.LANGUAGE_CODES:
            res[localized_field("to_country", lang)] = getattr(
                self.to_country, localized_field("name", lang)
            )

        return res

    def __unicode__(self):
        return "%s у %s" % (self.get_relationship_type_display(), self.to_country)

    class Meta:
        verbose_name = _("Зв'язок з країною")
        verbose_name_plural = _("Зв'язки з країнами")


class RelationshipProof(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    proof_title = models.TextField(
        _("Назва доказу зв'язку"),
        blank=True,
        help_text=_("Наприклад: склад ВР 7-го скликання"),
    )

    proof_document = models.ForeignKey(
        "core.Document",
        verbose_name=_("Документ-доказ зв'язку"),
        default=None,
        blank=True,
        null=True,
    )
    proof = models.TextField(_("або посилання на доказ зв'язку"), blank=True)

    def clean(self):
        if self.proof_document is None and not self.proof:
            raise ValidationError(
                {
                    "proof_document": _(
                        "Поле документа або посилання має бути заповнено"
                    ),
                    "proof": _("Поле документа або посилання має бути заповнено"),
                }
            )

        if self.proof_document is not None and self.proof:
            raise ValidationError(
                {
                    "proof_document": _(
                        "Тільки поле документа або посилання має бути заповнено"
                    ),
                    "proof": _(
                        "Тільки поле документа або посилання має бути заповнено"
                    ),
                }
            )

    def __unicode__(self):
        return "%s: %s" % (self.proof_title, self.proof_document or self.proof)

    class Meta:
        verbose_name = _("Підтвердження зв'язку")
        verbose_name_plural = _("Підтвердження зв'язків")
