# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from core.utils import render_date


class AbstractNode(object):
    def get_node_info(self, with_connections=False):
        t = type(self)
        if t is models.DEFERRED:
            t = t.__base__

        return {
            "pk": self.pk,
            "model": t._meta.model_name,
            "details": reverse(
                "connections",
                kwargs={
                    "model": t._meta.model_name,
                    "obj_id": self.pk
                }
            ),
            "kind": "",
            "description": "",
            "connections": []
        }


class AbstractRelationship(models.Model):
    date_established = models.DateField(
        _("Зв'язок почався"), blank=True, null=True)

    date_established_details = models.IntegerField(
        _("точність"),
        choices=(
            (0, _("Точна дата")),
            (1, _("Рік та місяць")),
            (2, _("Тільки рік")),
        ),
        default=0)

    date_finished = models.DateField(
        _("Зв'язок скінчився"), blank=True, null=True)

    date_finished_details = models.IntegerField(
        _("точність"),
        choices=(
            (0, _("Точна дата")),
            (1, _("Рік та місяць")),
            (2, _("Тільки рік")),
        ),
        default=0)

    date_confirmed = models.DateField(
        _("Підтверджено"), blank=True, null=True)

    date_confirmed_details = models.IntegerField(
        _("точність"),
        choices=(
            (0, _("Точна дата")),
            (1, _("Рік та місяць")),
            (2, _("Тільки рік")),
        ),
        default=0)

    @property
    def date_established_human(self):
        return render_date(self.date_established,
                           self.date_established_details)

    @property
    def date_finished_human(self):
        return render_date(self.date_finished,
                           self.date_finished_details)

    @property
    def date_confirmed_human(self):
        return render_date(self.date_confirmed,
                           self.date_confirmed_details)

    proofs = GenericRelation("RelationshipProof")

    proof_title = models.TextField(
        _("Назва доказу зв'язку"), blank=True,
        help_text="Наприклад: склад ВР 7-го скликання")
    proof = models.TextField(_("Посилання на доказ зв'язку"), blank=True)

    @property
    def has_additional_info(self):
        if any([self.date_confirmed, self.date_established, self.date_finished]):
            return True

        return bool(self.proofs.count())

    class Meta:
        abstract = True
