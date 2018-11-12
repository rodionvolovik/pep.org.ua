# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from unicodecsv import DictReader


def load_countries(apps, schema_editor):
    country = apps.get_model("core", "Country")

    with open("core/dicts/countries.csv", "r") as fp:
        r = DictReader(fp)

        for l in r:
            country.objects.update_or_create(
                pk=l["Code"],
                iso2=l["Alpha 2"],
                iso3=l["Alpha 3"],
                name_ua=l["UA"],
                name_en=l["UK"],
            )


class Migration(migrations.Migration):

    dependencies = [("core", "0003_auto_20150227_0256")]

    operations = [migrations.RunPython(load_countries)]
