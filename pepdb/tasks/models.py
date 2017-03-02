# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from core.models import Person
from jsonfield import JSONField


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
    candidates_json = JSONField(verbose_name="Кандідати", null=True)
    edrpou_match = models.CharField(
        "Знайдена компанія", max_length=15, null=True, blank=True)
    company_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = "Результати пошуку компанії"
        verbose_name_plural = "Результати пошуку компаній"
