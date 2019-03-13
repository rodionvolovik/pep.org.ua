# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Ua2RuDictionary(models.Model):
    term = models.CharField("Термін", max_length=255, unique=True)
    translation = models.CharField(_("Переклад російською"), max_length=255, blank=True)
    alt_translation = models.CharField(
        _("Альтернативний переклад"), max_length=255, blank=True
    )
    comments = models.CharField(_("Коментарі"), blank=True, max_length=100)

    def __unicode__(self):
        return self.term

    class Meta:
        verbose_name = _("Переклад російською")
        verbose_name_plural = _("Переклади російською")


class Ua2EnDictionary(models.Model):
    term = models.CharField(_("Термін"), max_length=768, unique=True)
    translation = models.CharField(
        _("Переклад англійською"), max_length=768, blank=True
    )
    alt_translation = models.CharField(
        _("Альтернативний переклад"), max_length=768, blank=True
    )
    comments = models.CharField(_("Коментарі"), blank=True, max_length=100)

    def __unicode__(self):
        return self.term

    class Meta:
        verbose_name = _("Переклад англійською")
        verbose_name_plural = _("Переклади англійською")
        unique_together = [["term", "translation"]]
