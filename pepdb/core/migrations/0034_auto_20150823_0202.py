# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from unicodecsv import reader
from string import capwords


def title(s):
    chunks = s.split()
    chunks = map(lambda x: capwords(x, "-"), chunks)
    return " ".join(chunks)


def import_csv(model, fname, comment):
    with open(fname, "r") as fp:
        r = reader(fp)

        for l in r:
            model.objects.update_or_create(
                term=title(l[0]), translation=title(l[1]), comments=comment
            )


def load_dicts(apps, schema_editor):
    dct = apps.get_model("core", "Ua2RuDictionary")
    import_csv(dct, "core/dicts/extra.csv", "Екстра")


class Migration(migrations.Migration):

    dependencies = [("core", "0033_auto_20150807_0251")]

    operations = [migrations.RunPython(load_dicts)]
