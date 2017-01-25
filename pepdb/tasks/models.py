# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from core.models import Person


class PersonDeduplication(models.Model):
    person1 = models.ForeignKey(
        Person, verbose_name="Персона 1",
        related_name="task_ent_1")

    person2 = models.ForeignKey(
        Person, verbose_name="Персона 2",
        related_name="task_ent_2")

    user = models.ForeignKey(
        User, verbose_name="Користувач",
        blank=True, null=True)

    timestamp = models.DateTimeField(
        verbose_name="Дата та час", auto_now_add=True)

    class Meta:
        verbose_name = "Дублікат фізичних осіб"
        verbose_name_plural = "Дублікати фізичних осіб"
