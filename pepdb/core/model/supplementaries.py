# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy


class Document(models.Model):
    doc = models.FileField("Файл", upload_to="documents", max_length=1000)
    name = models.CharField("Людська назва", max_length=255)
    uploaded = models.DateTimeField("Був завантажений", auto_now=True)
    source = models.CharField("Першоджерело", blank=True, max_length=255)
    uploader = models.ForeignKey(User, verbose_name="Хто завантажив",
                                 related_name="pep_document")
    hash = models.CharField("Хеш", max_length=40, blank=True)
    comments = models.TextField("Коментарі", blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документи"


class FeedbackMessage(models.Model):
    person = models.CharField(
        ugettext_lazy("Про кого"), max_length=150, blank=True)
    text = models.TextField(
        ugettext_lazy("Інформація"), blank=False)
    link = models.URLField(
        ugettext_lazy("Підтвердження"), max_length=512, blank=True)
    contacts = models.TextField(
        ugettext_lazy("Контакти"), max_length=512, blank=True)
    read = models.BooleanField(ugettext_lazy("Прочитано"), default=False)
    added = models.DateTimeField("Був надісланий", auto_now=True)

    class Meta:
        verbose_name = "Зворотній зв'язок"
        verbose_name_plural = "Зворотній зв'язок"


class ActionLog(models.Model):
    user = models.ForeignKey(User, verbose_name="Користувач")
    action = models.CharField(verbose_name="Дія", max_length=30)
    timestamp = models.DateTimeField(
        verbose_name="Дата та час", auto_now_add=True)
    details = models.TextField(verbose_name="Деталі", blank=True)

    class Meta:
        verbose_name = "Дія користувача"
        verbose_name_plural = "Дії користувачів"

        index_together = [
            ["user", "action", "timestamp"],
        ]
