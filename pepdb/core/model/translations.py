# coding: utf-8
from __future__ import unicode_literals

from django.db import models


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
