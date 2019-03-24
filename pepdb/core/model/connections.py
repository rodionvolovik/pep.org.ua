# coding: utf-8
from __future__ import unicode_literals
from collections import OrderedDict


from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext_noop
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
            (ugettext_noop("чоловік"), [ugettext_noop("дружина")]),
            (ugettext_noop("дружина"), [ugettext_noop("чоловік")]),
            (ugettext_noop("чоловік/дружина"), [ugettext_noop("чоловік/дружина")]),
            (ugettext_noop("батько"), [ugettext_noop("син"), ugettext_noop("дочка"), ugettext_noop("син/дочка")]),
            (ugettext_noop("мати"), [ugettext_noop("син"), ugettext_noop("дочка"), ugettext_noop("син/дочка")]),
            (ugettext_noop("батько/мати"), [ugettext_noop("син"), ugettext_noop("дочка"), ugettext_noop("син/дочка")]),
            (ugettext_noop("син"), [ugettext_noop("батько"), ugettext_noop("мати"), ugettext_noop("батько/мати")]),
            (ugettext_noop("дочка"), [ugettext_noop("батько"), ugettext_noop("мати"), ugettext_noop("батько/мати")]),
            (ugettext_noop("син/дочка"), [ugettext_noop("батько"), ugettext_noop("мати"), ugettext_noop("батько/мати")]),
            (ugettext_noop("вітчим"), [ugettext_noop("пасинок"), ugettext_noop("падчерка")]),
            (ugettext_noop("мачуха"), [ugettext_noop("пасинок"), ugettext_noop("падчерка")]),
            (ugettext_noop("пасинок"), [ugettext_noop("вітчим"), ugettext_noop("мачуха")]),
            (ugettext_noop("падчерка"), [ugettext_noop("вітчим"), ugettext_noop("мачуха")]),
            (ugettext_noop("рідний брат"), [ugettext_noop("рідна сестра"), ugettext_noop("рідний брат")]),
            (ugettext_noop("рідна сестра"), [ugettext_noop("рідна сестра"), ugettext_noop("рідний брат")]),
            (ugettext_noop("дід"), [ugettext_noop("внук"), ugettext_noop("внучка")]),
            (ugettext_noop("баба"), [ugettext_noop("внук"), ugettext_noop("внучка")]),
            (ugettext_noop("прадід"), [ugettext_noop("правнук"), ugettext_noop("правнучка")]),
            (ugettext_noop("прабаба"), [ugettext_noop("правнук"), ugettext_noop("правнучка")]),
            (ugettext_noop("внук"), [ugettext_noop("дід"), ugettext_noop("баба")]),
            (ugettext_noop("внучка"), [ugettext_noop("дід"), ugettext_noop("баба")]),
            (ugettext_noop("правнук"), [ugettext_noop("прадід"), ugettext_noop("прабаба")]),
            (ugettext_noop("правнучка"), [ugettext_noop("прадід"), ugettext_noop("прабаба")]),
            (ugettext_noop("зять"), [ugettext_noop("теща"), ugettext_noop("тесть")]),
            (ugettext_noop("невістка"), [ugettext_noop("свекор"), ugettext_noop("свекруха")]),
            (ugettext_noop("тесть"), [ugettext_noop("зять")]),
            (ugettext_noop("теща"), [ugettext_noop("зять")]),
            (ugettext_noop("свекор"), [ugettext_noop("невістка")]),
            (ugettext_noop("свекруха"), [ugettext_noop("невістка")]),
            (ugettext_noop("усиновлювач"), [ugettext_noop("усиновлений")]),
            (ugettext_noop("усиновлений"), [ugettext_noop("усиновлювач")]),
            (
                ugettext_noop("опікун чи піклувальник"),
                [ugettext_noop("особа, яка перебуває під опікою або піклуванням")],
            ),
            (
                ugettext_noop("особа, яка перебуває під опікою або піклуванням"),
                [ugettext_noop("опікун чи піклувальник")],
            ),
            (
                ugettext_noop("особи, які спільно проживають"),
                [ugettext_noop("особи, які спільно проживають")],
            ),
            (
                ugettext_noop("пов'язані спільним побутом і мають взаємні права та обов'язки"),
                [ugettext_noop("пов'язані спільним побутом і мають взаємні права та обов'язки")],
            ),
            (ugettext_noop("ділові зв'язки"), [ugettext_noop("ділові зв'язки")]),
            (ugettext_noop("особисті зв'язки"), [ugettext_noop("особисті зв'язки")]),
            (ugettext_noop("дядько"), [ugettext_noop("племінник"), ugettext_noop("племінниця")]),
            (ugettext_noop("тітка"), [ugettext_noop("племінник"), ugettext_noop("племінниця")]),
            (ugettext_noop("племінник"), [ugettext_noop("дядько"), ugettext_noop("тітка")]),
            (ugettext_noop("племінниця"), [ugettext_noop("дядько"), ugettext_noop("тітка")]),
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
        ugettext_noop("Президент"),
        ugettext_noop("Прем’єр-міністр"),
        ugettext_noop("Міністр"),
        ugettext_noop("Перший заступник міністра"),
        ugettext_noop("Заступник міністра"),
        ugettext_noop("Керівник"),
        ugettext_noop("Перший заступник керівника"),
        ugettext_noop("Заступник керівника"),
        ugettext_noop("Народний депутат"),
        ugettext_noop("Голова"),
        ugettext_noop("Заступник Голови"),
        ugettext_noop("Перший заступник Голови"),
        ugettext_noop("Член Правління"),
        ugettext_noop("Член Ради"),
        ugettext_noop("Суддя"),
        ugettext_noop("Член"),
        ugettext_noop("Генеральний прокурор"),
        ugettext_noop("Заступник Генерального прокурора"),
        ugettext_noop("Надзвичайний і повноважний посол"),
        ugettext_noop("Головнокомандувач"),
        ugettext_noop("Службовець першої категорії посад"),
        ugettext_noop("Член центрального статутного органу"),
        ugettext_noop("Повірений у справах"),
        ugettext_noop("Засновник/учасник"),
        ugettext_noop("Колишній засновник/учасник"),
        ugettext_noop("Бенефіціарний власник"),
        ugettext_noop("Номінальний власник"),
        ugettext_noop("Номінальний директор"),
        ugettext_noop("Фінансові зв'язки"),
        ugettext_noop("Секретар"),
        ugettext_noop("Керуючий"),
        ugettext_noop("Контролер"),
        ugettext_noop("Клієнт"),
        ugettext_noop("Клієнт банку"),
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
        max_digits=16,
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

            term = get_localized_field(self, "relationship_type", settings.LANGUAGE_CODE)
            trans = get_localized_field(self, "relationship_type", lang)

            if term and (term == trans or not trans):
                val = translate_through_dict(
                    term,
                    settings.LANGUAGE_CODE,
                    lang,
                )

                if val is not None:
                    setattr(self, localized_field("relationship_type", lang), val)
                else:
                    setattr(
                        self,
                        localized_field("relationship_type", lang),
                        "",
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
        _("Акціонер"),
        _("Головна компанія"),
        _("Філія"),
        _("Керуюча компанія"),
        _("Керована компанія"),
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
        _("Акціонер"): _("Підконтрольна"),
        _("Головна компанія"): _("Філія"),
        _("Філія"): _("Головна компанія"),
        _("Керуюча компанія"): _("Керована компанія"),
        _("Керована компанія"): _("Керуюча компанія"),
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
        _("Частка власності (відсотки)"), blank=True, null=True
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
        _("Назва документа або посилання"),
        blank=True,
        help_text=_("Наприклад: склад ВР 7-го скликання"),
    )

    proof_document = models.ForeignKey(
        "core.Document",
        verbose_name=_("Файл документа"),
        default=None,
        blank=True,
        null=True,
    )
    proof = models.TextField(_("або посилання"), blank=True)

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
        verbose_name = _("Посилання або документ")
        verbose_name_plural = _("Посилання або документи")
