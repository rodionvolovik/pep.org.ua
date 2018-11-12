# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_meta_countries(apps, schema_editor):
    Country = apps.get_model("core", "Country")

    Country.objects.get_or_create(
        name_ua="Європейський союз",
        name_en="European Union",
        iso2="EU",
        iso3="",
        is_jurisdiction=True,
    )

    Country.objects.get_or_create(
        name_ua="Організація Об'єднаних Націй",
        name_en="United Nations",
        iso2="UN",
        iso3="",
        is_jurisdiction=True,
    )


class Migration(migrations.Migration):

    dependencies = [("core", "0023_auto_20150415_0202")]

    operations = [migrations.RunPython(add_meta_countries)]
