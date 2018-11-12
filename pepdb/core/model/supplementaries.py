# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Document(models.Model):
    doc = models.FileField(_("Файл"), upload_to="documents", max_length=1000)
    name = models.CharField(_("Людська назва"), max_length=255)
    uploaded = models.DateTimeField(_("Був завантажений"), auto_now=True)
    source = models.CharField(_("Першоджерело"), blank=True, max_length=255)
    uploader = models.ForeignKey(
        User, verbose_name=_("Хто завантажив"), related_name="pep_document"
    )
    hash = models.CharField(_("Хеш"), max_length=40, blank=True)
    comments = models.TextField(_("Коментарі"), blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains", "source__icontains")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Документ")
        verbose_name_plural = _("Документи")


class FeedbackMessage(models.Model):
    person = models.CharField(_("Про кого"), max_length=150, blank=True)
    text = models.TextField(_("Інформація"), blank=False)
    link = models.URLField(_("Підтвердження"), max_length=512, blank=True)
    email = models.EmailField(_("e-mail"), max_length=512, blank=True)
    contacts = models.TextField(_("Контакти"), max_length=512, blank=True)
    read = models.BooleanField(_("Прочитано"), default=False)
    added = models.DateTimeField(_("Був надісланий"), auto_now=True)

    answered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_("Відповів"),
        blank=True,
        null=True,
    )
    answer_added = models.DateTimeField(_("Була надіслана"), blank=True, null=True)
    short_answer = models.TextField(_("Суть відповіді"), blank=True, null=True)

    class Meta:
        verbose_name = _("Зворотній зв'язок")
        verbose_name_plural = _("Зворотній зв'язок")


class ActionLog(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Користувач"))
    action = models.CharField(verbose_name=_("Дія"), max_length=30)
    timestamp = models.DateTimeField(verbose_name=_("Дата та час"), auto_now_add=True)
    details = models.TextField(verbose_name=_("Деталі"), blank=True)

    class Meta:
        verbose_name = _("Дія користувача")
        verbose_name_plural = _("Дії користувачів")

        index_together = [["user", "action", "timestamp"]]
