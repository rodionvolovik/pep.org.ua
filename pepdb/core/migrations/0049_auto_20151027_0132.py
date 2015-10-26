# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from unicodecsv import reader


def import_csv(model, fname, comment):
    with open(fname, "r") as fp:
        r = reader(fp)

        for l in r:
            model.objects.update_or_create(
                term=l[0],
                translation=l[5],
                comments=comment
            )


def load_dicts(apps, schema_editor):
    dct = apps.get_model("core", "Ua2EnDictionary")
    dct.objects.all().delete()
    import_csv(dct, "core/dicts/companies.csv", "Компанії")
    import_csv(dct, "core/dicts/positions.csv", "Посади")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_auto_20151026_1541'),
    ]

    operations = [
        migrations.RunPython(
            load_dicts, reverse_code=migrations.RunPython.noop),
    ]
