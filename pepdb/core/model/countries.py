# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, activate, deactivate

from core.model.base import AbstractNode


class Country(models.Model, AbstractNode):
    name = models.CharField(_("Назва"), max_length=100)
    iso2 = models.CharField(_("iso2 код"), max_length=2, blank=True)
    iso3 = models.CharField(_("iso3 код"), max_length=3, blank=True)
    is_jurisdiction = models.BooleanField(_("Не є країною"), default=False)

    def __unicode__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name_en__icontains", "name_uk__icontains")

    def get_absolute_url(self):
        return reverse("countries", kwargs={"country_id": self.iso2})

    def localized_url(self, locale):
        activate(locale)
        url = self.get_absolute_url()
        deactivate()
        return url

    @property
    def url_uk(self):
        return settings.SITE_URL + self.localized_url("uk")

    class Meta:
        verbose_name = _("Країна/юрісдикція")
        verbose_name_plural = _("Країни/юрісдикції")

    def get_node_info(self, with_connections=False):
        res = super(Country, self).get_node_info(with_connections)
        res["name"] = self.name

        if with_connections:
            connections = []

            persons = self.person2country_set.select_related("from_person")
            for p in persons:
                connections.append(
                    {
                        "relation": unicode(
                            ugettext_lazy(p.get_relationship_type_display())
                        ),
                        "node": p.from_person.get_node_info(False),
                        "model": p._meta.model_name,
                        "pk": p.pk,
                    }
                )

            companies = self.company2country_set.select_related("from_company")
            for c in companies:
                connections.append(
                    {
                        "relation": unicode(
                            ugettext_lazy(c.get_relationship_type_display())
                        ),
                        "node": c.from_company.get_node_info(False),
                        "model": c._meta.model_name,
                        "pk": c.pk,
                    }
                )

            res["connections"] = connections

        return res
