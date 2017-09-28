# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from core.models import Person
from jsonfield import JSONField
from django.contrib.postgres.fields import ArrayField


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

    status = models.CharField(
        "Статус",
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_index=True
    )

    company_key = models.CharField(
        "Ключ компанії", max_length=500, unique=True)

    person = models.IntegerField("Власник в реєстрі PEP")
    person_json = JSONField(verbose_name="Власник в реєстрі PEP", null=True)
    is_family_member = models.BooleanField("Член родини")

    declarations = ArrayField(
        models.IntegerField(),
        verbose_name="Декларації, що підтверджують зв'язок",
        null=True,
        blank=True
    )

    pep_company_information = JSONField("Записи компанії, згруповані разом")
    candidates_json = JSONField(verbose_name="Кандидати на матчінг", null=True)
    edrpou_match = models.CharField(
        "Знайдена компанія", max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = "Бенефіціари компаній"
        verbose_name_plural = "Бенефіціари компаній"


class CompanyDeduplication(AbstractTask):
    STATUS_CHOICES = (
        ("p", "Не перевірено"),
        ("m", "Об'єднати"),
        ("a", "Залишити все як є"),
        ("p1", "Перша є правонаступницею"),
        ("p2", "Друга є правонаступницею"),
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
