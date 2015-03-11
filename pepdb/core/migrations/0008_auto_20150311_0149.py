# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from unicodecsv import reader
from string import capwords


def title(s):
    chunks = s.split()
    chunks = map(lambda x: capwords(x, u"-"), chunks)
    return u" ".join(chunks)


def import_csv(model, fname, comment):
    with open(fname, "r") as fp:
        r = reader(fp)

        for l in r:
            if l[-1] == "!":
                continue

            model.objects.update_or_create(
                term=title(l[0]),
                translation=title(l[1]),
                alt_translation=title(l[2]),
                comments=comment
            )


def load_dicts(apps, schema_editor):
    dct = apps.get_model("core", "Ua2RuDictionary")
    import_csv(dct, "core/dicts/names.csv", "Ім'я")
    import_csv(dct, "core/dicts/patronymics.csv", "По-батькові")
    import_csv(dct, "core/dicts/lastnames.csv", "Прізвище")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150311_0141'),
    ]

    operations = [
        migrations.RunPython(load_dicts),
    ]
