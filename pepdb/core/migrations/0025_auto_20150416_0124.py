# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def rename(apps, schema_editor):
    Document = apps.get_model("core", "Document")

    for d in Document.objects.all():
        if not d.name_ua:
            d.name_ua = d.name
            d.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20150415_0202'),
    ]

    operations = [
        migrations.RunPython(rename),
    ]
