# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from core.models import Person
from django.contrib.postgres.fields import JSONField as DjangoJSONField
from jsonfield import JSONField
from jsonfield.encoder import JSONEncoder
from django.contrib.postgres.fields import ArrayField


# Custom dump kwargs for third party lib for jsonfield, uses ensure_ascii=False
# to enable search of cyrillic in the db
dump_kwargs = {
    'cls': JSONEncoder,
    'separators': (',', ':'),
    'ensure_ascii': False
}

class AbstractTask(models.Model):
    user = models.ForeignKey(
        User, verbose_name="Користувач",
        blank=True, null=True)

    timestamp = models.DateTimeField(
        verbose_name="Створено", auto_now_add=True)

    last_modified = models.DateTimeField(
        verbose_name="Змінено", auto_now=True, null=True)

    class Meta:
        abstract = True


class PersonDeduplication(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("m", "Об'єднати"),
        ("a", "Залишити все як є"),
        ("-", "---------------"),   # That's a shame, I know
        ("d1", "Видалити першу"),
        ("d2", "Видалити другу"),
        ("dd", "Видалити всі"),
    )

    status = models.CharField(
        "Статус",
        max_length=2,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    person1_id = models.IntegerField(null=True)
    person2_id = models.IntegerField(null=True)
    fuzzy = models.BooleanField(default=False, db_index=True)
    applied = models.BooleanField(default=False, db_index=True)

    person1_json = JSONField(verbose_name="Персона 1", null=True)
    person2_json = JSONField(verbose_name="Персона 2", null=True)

    class Meta:
        verbose_name = "Дублікат фізичних осіб"
        verbose_name_plural = "Дублікати фізичних осіб"

        unique_together = [
            ["person1_id", "person2_id"],
        ]


class CompanyMatching(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("r", "Потребує додаткової перевірки"),
        ("m", "Виконано"),
    )

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    company_json = JSONField(verbose_name="Компанія", null=True)
    candidates_json = JSONField(verbose_name="Кандидати", null=True)
    edrpou_match = models.CharField(
        "Знайдена компанія", max_length=15, null=True, blank=True)
    company_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = "Результати пошуку компанії"
        verbose_name_plural = "Результати пошуку компаній"


class BeneficiariesMatching(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("r", "Потребує перевірки"),
        ("m", "Виконано"),
        ("n", "Закордонна компанія, не знайдено"),
        ("y", "Закордонна компанія, знайдено"),
    )
    TYPE_CHOICES = (
        ("b", "Бенефіціарний власник"),
        ("f", "Засновник"),
        ("s", "Акціонер"),
    )

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    type_of_connection = models.CharField(
        "Тип зв'язку",
        max_length=1,
        choices=TYPE_CHOICES,
        default="b",
        db_index=True
    )

    company_key = models.CharField(
        "Ключ компанії", max_length=500)

    person = models.IntegerField("Власник в реєстрі PEP")
    person_json = JSONField(verbose_name="Власник в реєстрі PEP", null=True, dump_kwargs=dump_kwargs)

    is_family_member = models.BooleanField("Член родини")

    declarations = ArrayField(
        models.IntegerField(),
        verbose_name="Декларації, що підтверджують зв'язок",
        null=True,
        blank=True
    )

    pep_company_information = JSONField("Записи компанії, згруповані разом", dump_kwargs=dump_kwargs)
    candidates_json = JSONField(verbose_name="Кандидати на матчінг", null=True, dump_kwargs=dump_kwargs)
    edrpou_match = models.CharField(
        "Знайдена компанія", max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = "Бенефіціар або власник компанії"
        verbose_name_plural = "Бенефіціари або власники компаній"
        unique_together = [
            ["company_key", "type_of_connection"],
        ]


class CompanyDeduplication(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("m", "Об'єднати"),
        ("a", "Залишити все як є"),
        ("-", "---------------"),   # That's a shame and copy-pasted, I know
        ("d1", "Видалити першу"),
        ("d2", "Видалити другу"),
        ("dd", "Видалити всі"),
    )

    status = models.CharField(
        "Статус",
        max_length=2,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    company1_id = models.IntegerField(null=True)
    company2_id = models.IntegerField(null=True)
    fuzzy = models.BooleanField(default=False, db_index=True)
    applied = models.BooleanField(default=False, db_index=True)

    company1_json = JSONField(verbose_name="Компанія 1", null=True)
    company2_json = JSONField(verbose_name="Компанія 2", null=True)

    class Meta:
        verbose_name = "Дублікат юридичних осіб"
        verbose_name_plural = "Дублікати юридичних осіб"

        unique_together = [
            ["company1_id", "company2_id"],
        ]

        index_together = [
            ["company1_id", "company2_id"],
        ]


class EDRMonitoring(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("a", "Застосувати зміну"),
        ("i", "Ігнорувати зміну"),
        ("r", "Потребує додаткової перевірки"),
    )

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    # Holy four
    pep_name = models.CharField(
        "Прізвище керівника з БД ПЕП", max_length=200, null=True, blank=True)
    pep_position = models.CharField(
        "Посада керівника з БД ПЕП", max_length=200, null=True, blank=True)
    company_edrpou = models.CharField(
        "ЄДРПОУ компанії з БД ПЕП", max_length=15, null=True, blank=True)
    edr_name = models.CharField(
        "Прізвище керівника з ЄДР", max_length=200, null=True, blank=True)

    pep_company_json = JSONField(verbose_name="Компанія де ПЕП є керівником", null=True)
    edr_company_json = JSONField(verbose_name="Компанія з ЄДР", null=True)
    name_match_score = models.IntegerField("Ступінь співпадіння")

    company_id = models.IntegerField(null=True)
    person_id = models.IntegerField(null=True)
    relation_id = models.IntegerField(null=True)

    applied = models.BooleanField(verbose_name="Застосовано", default=False, db_index=True)
    edr_date = models.DateField(verbose_name="Дата експорту з ЄДР")

    class Meta:
        verbose_name = "Результат моніторингу ЄДР"
        verbose_name_plural = "Результати моніторингу ЄДР"

        unique_together = [
            ["pep_name", "pep_position", "edr_name", "company_edrpou"],
        ]

        index_together = [
            ["pep_name", "pep_position", "edr_name", "company_edrpou"],
        ]


# Cheezy throwaway model
class TerminationNotice(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("a", "Застосувати зміну"),
        ("i", "Ігнорувати зміну"),
        ("r", "Потребує додаткової перевірки"),
    )

    ACTION_CHOICES = (
        ("review", "Перевірити вручну"),
        ("change_type", "Змінити тип ПЕП на пов'язану особу"),
        ("change_and_fire", "Змінити тип ПЕП на пов'язану особу та встановити дату"),
        ("fire", "Припинити ПЕПство"),
        ("fire_related", "Припинити ПЕПство пов'язаної особи"),
    )

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    new_person_status = models.IntegerField(
        "Можлива причина припинення статусу ПЕП",
        choices=Person._reasons_of_termination,
        blank=True,
        null=True
    )

    action = models.CharField(
        "Дія",
        max_length=25,
        choices=ACTION_CHOICES,
        default="fire",
        db_index=True
    )

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

    termination_date_ceiled = models.DateField(
        "Дата припинення статусу ПЕП, округлена вгору",
        blank=True, null=True
    )

    comments = models.TextField(
        "Коментар",
        blank=True
    )

    pep_name = models.CharField(
        "Прізвище", max_length=200, null=True, blank=True)
    pep_position = models.TextField("Посада", null=True, blank=True)

    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)
    applied = models.BooleanField(verbose_name="Застосовано", default=False, db_index=True)

    class Meta:
        verbose_name = "Кандидат на виліт"
        verbose_name_plural = "Кандидати на виліт"

        unique_together = [
            ["person", "pep_name", "termination_date", "termination_date_details"],
        ]

        index_together = [
            ["person", "pep_name", "termination_date", "termination_date_details"],
        ]


class AdHocMatch(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("a", "Застосовано"),
        ("i", "Ігнорувати"),
        ("r", "Потребує додаткової перевірки"),
    )

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    pep_name = models.CharField(
        "Прізвище", max_length=200, null=True, blank=True)
    pep_position = models.TextField("Посада", null=True, blank=True)
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL, related_name="adhoc_matches")
    matched_json_hash = models.CharField("Хеш", max_length=40)
    matched_json = DjangoJSONField(verbose_name="Знайдено в датасеті", null=True)
    dataset_id = models.CharField("Походження датасету", max_length=200, null=True, blank=True)
    name_match_score = models.IntegerField("Ступінь співпадіння")
    name_in_dataset = models.CharField(
        "ПІБ з датасету", max_length=200, null=True, blank=True)

    applied = models.BooleanField(
        "Матч було застосовано", default=False
    )

    last_updated_from_dataset = models.DateTimeField(
        verbose_name="Останній раз завантажено", null=True)

    first_updated_from_dataset = models.DateTimeField(
        verbose_name="Перший раз завантажено", null=True)

    class Meta:
        verbose_name = "Універсальний матчінг"
        verbose_name_plural = "Універсальні матчінги"


class WikiMatch(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("a", "Застосовано"),
        ("i", "Ігнорувати"),
        ("r", "Потребує додаткової перевірки"),
    )

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    pep_name = models.CharField(
        "Прізвище", max_length=200, null=True, blank=True)
    pep_position = models.TextField("Посада", null=True, blank=True)
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL, related_name="wiki_matches")
    matched_json = DjangoJSONField(verbose_name="Сутності, знайдені у вікі", null=True)
    wikidata_id = models.CharField("Коректний WikiData ID", max_length=50, blank=True)

    class Meta:
        verbose_name = "Матчінг з WikiData"
        verbose_name_plural = "Матчінги з WikiData"
