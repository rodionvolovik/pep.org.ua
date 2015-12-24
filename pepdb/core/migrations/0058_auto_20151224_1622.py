# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def _delete_duplicates(model):
    for term in model.objects.distinct("term").values_list("term", flat=True):
        translations = list(model.objects.filter(term=term))

        for t in translations[1:]:
            print(t.term + ": " + t.translation)
            t.delete()


def delete_duplicates(apps, schema_editor):
    _delete_duplicates(apps.get_model('core.Ua2RuDictionary'))
    _delete_duplicates(apps.get_model('core.Ua2EnDictionary'))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20151128_0248'),
    ]

    operations = [
        migrations.RunPython(delete_duplicates),
    ]
