# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField as DjangoJSONField
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField
from jsonfield.encoder import JSONEncoder

from core.models import Person


# Custom dump kwargs for third party lib for jsonfield, uses ensure_ascii=False
# to enable search of cyrillic in the db
dump_kwargs = {"cls": JSONEncoder, "separators": (",", ":"), "ensure_ascii": False}


class AbstractTask(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Користувач"), blank=True, null=True)

    timestamp = models.DateTimeField(verbose_name=_("Створено"), auto_now_add=True)

    last_modified = models.DateTimeField(
        verbose_name=_("Змінено"), auto_now=True, null=True
    )

    class Meta:
        abstract = True


class PersonDeduplication(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("m", _("Об'єднати")),
        ("a", "Залишити все як є"),
        ("-", "---------------"),  # That's a shame, I know
        ("d1", _("Видалити першу")),
        ("d2", _("Видалити другу")),
        ("dd", _("Видалити всі")),
    )

    status = models.CharField(
        _("Статус"), max_length=2, choices=STATUS_CHOICES, default="p", db_index=True
    )

    person1_id = models.IntegerField(null=True)
    person2_id = models.IntegerField(null=True)
    fuzzy = models.BooleanField(default=False, db_index=True)
    applied = models.BooleanField(default=False, db_index=True)

    person1_json = JSONField(verbose_name=_("Персона 1"), null=True)
    person2_json = JSONField(verbose_name=_("Персона 2"), null=True)

    class Meta:
        verbose_name = _("Дублікат фізичних осіб")
        verbose_name_plural = _("Дублікати фізичних осіб")

        unique_together = [["person1_id", "person2_id"]]


class CompanyMatching(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("r", _("Потребує додаткової перевірки")),
        ("m", _("Виконано")),
    )

    status = models.CharField(
        _("Статус"), max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    company_json = JSONField(verbose_name=_("Компанія"), null=True)
    candidates_json = JSONField(verbose_name=_("Кандидати"), null=True)
    edrpou_match = models.CharField(
        _("Знайдена компанія"), max_length=15, null=True, blank=True
    )
    company_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = _("Результати пошуку компанії")
        verbose_name_plural = _("Результати пошуку компаній")


class BeneficiariesMatching(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("r", _("Потребує перевірки")),
        ("m", _("Виконано")),
        ("n", _("Закордонна компанія, не знайдено")),
        ("y", _("Закордонна компанія, знайдено")),
    )
    TYPE_CHOICES = (
        ("b", _("Бенефіціарний власник")),
        ("f", _("Засновник")),
        ("s", _("Акціонер")),
    )

    status = models.CharField(
        _("Статус"), max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    type_of_connection = models.CharField(
        _("Тип зв'язку"), max_length=1, choices=TYPE_CHOICES, default="b", db_index=True
    )

    company_key = models.CharField(_("Ключ компанії"), max_length=500)

    person = models.IntegerField(_("Власник в реєстрі PEP"))
    person_json = JSONField(
        verbose_name=_("Власник в реєстрі PEP"), null=True, dump_kwargs=dump_kwargs
    )

    is_family_member = models.BooleanField(_("Член родини"))

    declarations = ArrayField(
        models.IntegerField(),
        verbose_name=_("Декларації, що підтверджують зв'язок"),
        null=True,
        blank=True,
    )

    pep_company_information = JSONField(
        _("Записи компанії, згруповані разом"), dump_kwargs=dump_kwargs
    )
    candidates_json = JSONField(
        verbose_name=_("Кандидати на матчінг"), null=True, dump_kwargs=dump_kwargs
    )
    edrpou_match = models.CharField(
        _("Знайдена компанія"), max_length=15, null=True, blank=True
    )

    class Meta:
        verbose_name = _("Бенефіціар або власник компанії")
        verbose_name_plural = _("Бенефіціари або власники компаній")
        unique_together = [["company_key", "type_of_connection"]]


class CompanyDeduplication(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("m", _("Об'єднати")),
        ("a", _("Залишити все як є")),
        ("-", "---------------"),  # That's a shame and copy-pasted, I know
        ("d1", _("Видалити першу")),
        ("d2", _("Видалити другу")),
        ("dd", _("Видалити всі")),
    )

    status = models.CharField(
        _("Статус"), max_length=2, choices=STATUS_CHOICES, default="p", db_index=True
    )

    company1_id = models.IntegerField(null=True)
    company2_id = models.IntegerField(null=True)
    fuzzy = models.BooleanField(default=False, db_index=True)
    applied = models.BooleanField(default=False, db_index=True)

    company1_json = JSONField(verbose_name=_("Компанія 1"), null=True)
    company2_json = JSONField(verbose_name=_("Компанія 2"), null=True)

    class Meta:
        verbose_name = _("Дублікат юридичних осіб")
        verbose_name_plural = _("Дублікати юридичних осіб")

        unique_together = [["company1_id", "company2_id"]]

        index_together = [["company1_id", "company2_id"]]


class EDRMonitoring(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("a", _("Застосувати зміну")),
        ("i", _("Ігнорувати зміну")),
        ("r", _("Потребує додаткової перевірки")),
    )

    status = models.CharField(
        _("Статус"), max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    # Holy four
    pep_name = models.CharField(
        _("Прізвище керівника з БД ПЕП"), max_length=200, null=True, blank=True
    )
    pep_position = models.CharField(
        _("Посада керівника з БД ПЕП"), max_length=200, null=True, blank=True
    )
    company_edrpou = models.CharField(
        _("ЄДРПОУ компанії з БД ПЕП"), max_length=15, null=True, blank=True
    )
    edr_name = models.CharField(
        _("Прізвище керівника з ЄДР"), max_length=200, null=True, blank=True
    )

    pep_company_json = JSONField(
        verbose_name=_("Компанія де ПЕП є керівником"), null=True
    )
    edr_company_json = JSONField(verbose_name=_("Компанія з ЄДР"), null=True)
    name_match_score = models.IntegerField(_("Ступінь співпадіння"))

    company_id = models.IntegerField(null=True)
    person_id = models.IntegerField(null=True)
    relation_id = models.IntegerField(null=True)

    applied = models.BooleanField(
        verbose_name=_("Застосовано"), default=False, db_index=True
    )
    edr_date = models.DateField(verbose_name=_("Дата експорту з ЄДР"))

    class Meta:
        verbose_name = _("Результат моніторингу ЄДР")
        verbose_name_plural = _("Результати моніторингу ЄДР")

        unique_together = [["pep_name", "pep_position", "edr_name", "company_edrpou"]]

        index_together = [["pep_name", "pep_position", "edr_name", "company_edrpou"]]


# Cheezy throwaway model
class TerminationNotice(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("a", _("Застосувати зміну")),
        ("i", _("Ігнорувати зміну")),
        ("r", _("Потребує додаткової перевірки")),
    )

    ACTION_CHOICES = (
        ("review", _("Перевірити вручну")),
        ("change_type", _("Змінити тип ПЕП на пов'язану особу")),
        ("change_and_fire", _("Змінити тип ПЕП на пов'язану особу та встановити дату")),
        ("fire", _("Припинити ПЕПство")),
        ("fire_related", _("Припинити ПЕПство пов'язаної особи")),
    )

    status = models.CharField(
        _("Статус"), max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    new_person_status = models.IntegerField(
        _("Можлива причина припинення статусу ПЕП"),
        choices=Person._reasons_of_termination,
        blank=True,
        null=True,
    )

    action = models.CharField(
        _("Дія"), max_length=25, choices=ACTION_CHOICES, default="fire", db_index=True
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

    termination_date_ceiled = models.DateField(
        _("Дата припинення статусу ПЕП, округлена вгору"), blank=True, null=True
    )

    comments = models.TextField(_("Коментар"), blank=True)

    pep_name = models.CharField(_("Прізвище"), max_length=200, null=True, blank=True)
    pep_position = models.TextField("Посада", null=True, blank=True)

    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)
    applied = models.BooleanField(
        verbose_name=_("Застосовано"), default=False, db_index=True
    )

    class Meta:
        verbose_name = _("Кандидат на виліт")
        verbose_name_plural = _("Кандидати на виліт")

        unique_together = [
            ["person", "pep_name", "termination_date", "termination_date_details"]
        ]

        index_together = [
            ["person", "pep_name", "termination_date", "termination_date_details"]
        ]


class AdHocMatch(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("a", _("Застосовано")),
        ("i", _("Ігнорувати")),
        ("r", _("Потребує додаткової перевірки")),
    )

    status = models.CharField(
        _("Статус"), max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    pep_name = models.CharField(_("Прізвище"), max_length=200, null=True, blank=True)
    pep_position = models.TextField(_("Посада"), null=True, blank=True)
    person = models.ForeignKey(
        Person, null=True, on_delete=models.SET_NULL, related_name="adhoc_matches"
    )
    matched_json_hash = models.CharField(_("Хеш"), max_length=40)
    matched_json = DjangoJSONField(verbose_name=_("Знайдено в датасеті"), null=True)
    dataset_id = models.CharField(
        _("Походження датасету"), max_length=200, null=True, blank=True
    )
    name_match_score = models.IntegerField(_("Ступінь співпадіння"))
    name_in_dataset = models.CharField(
        _("ПІБ з датасету"), max_length=200, null=True, blank=True
    )

    applied = models.BooleanField(_("Матч було застосовано"), default=False)

    last_updated_from_dataset = models.DateTimeField(
        verbose_name=_("Останній раз завантажено"), null=True
    )

    first_updated_from_dataset = models.DateTimeField(
        verbose_name=_("Перший раз завантажено"), null=True
    )

    class Meta:
        verbose_name = _("Універсальний матчінг")
        verbose_name_plural = _("Універсальні матчінги")


class WikiMatch(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("a", _("Застосовано")),
        ("i", _("Ігнорувати")),
        ("r", _("Потребує додаткової перевірки")),
    )

    status = models.CharField(
        "Статус", max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    pep_name = models.CharField(_("Прізвище"), max_length=200, null=True, blank=True)
    pep_position = models.TextField(_("Посада"), null=True, blank=True)
    person = models.ForeignKey(
        Person, null=True, on_delete=models.SET_NULL, related_name="wiki_matches"
    )
    matched_json = DjangoJSONField(
        verbose_name=_("Сутності, знайдені у вікі"), null=True
    )
    wikidata_id = models.CharField(
        _("Коректний WikiData ID"), max_length=50, blank=True
    )

    class Meta:
        verbose_name = _("Матчінг з WikiData")
        verbose_name_plural = _("Матчінги з WikiData")


class SMIDACandidate(AbstractTask):
    STATUS_CHOICES = (
        ("p", _("Не перевірено")),
        ("a", _("Застосовано")),
        ("i", _("Ігнорувати")),
        ("r", _("Потребує додаткової перевірки")),
    )

    POSITION_BODIES = (
        ("sc", _("Правління")),
        ("wc", _("Наглядова рада")),
        ("ac", _("Ревізійна комісія")),
        ("a", _("Бухгалтерія")),
        ("s", _("Секретаріат")),
        ("o", _("Інше")),
        ("h", _("Керівник")),
    )

    POSITION_CLASSES = (
        ("h", _("Голова")),
        ("d", _("Заступник голови")),
        ("m", _("Член")),
        ("a", _("Головний бухгалтер")),
        ("s", _("Корпоративний секретар")),
        ("o", _("Інше")),
    )

    status = models.CharField(
        _("Статус"), max_length=1, choices=STATUS_CHOICES, default="p", db_index=True
    )

    smida_edrpou = models.CharField(
        _("Код компанії"), max_length=15, null=True, blank=True
    )
    smida_company_name = models.CharField(
        _("Назва компанії"), max_length=200, null=True, blank=True
    )
    smida_level = models.IntegerField(_("Відстань"), null=True)
    smida_shares = models.FloatField(_("% держави"), null=True)

    smida_name = models.CharField(_("ПІБ зі звіту"), max_length=200, blank=True)
    smida_parsed_name = models.CharField(
        _("'Чистий 'ПІБ зі звіту"), max_length=200, blank=True
    )
    smida_dt = models.DateTimeField(_("Дата звіту"))
    smida_position = models.CharField(_("Посада зі звіту"), max_length=200, blank=True)
    smida_prev_position = models.TextField(_("Попередня посада"), blank=True)
    smida_yob = models.IntegerField(_("Рік народження"), null=True)

    smida_is_real_person = models.BooleanField(_("Фізособа"), default=True)
    smida_position_body = models.CharField(
        _("Орган"), max_length=2, choices=POSITION_BODIES
    )
    smida_position_class = models.CharField(
        _("Рівень"), max_length=1, choices=POSITION_CLASSES
    )

    matched_json = DjangoJSONField(verbose_name=_("Запис зі звіту"), null=True)
    matched_json_hash = models.CharField(_("Хеш"), max_length=40, null=True)

    class Meta:
        verbose_name = _("Матчінг зі звітами SMIDA")
        verbose_name_plural = _("Матчінги зі звітами SMIDA")
