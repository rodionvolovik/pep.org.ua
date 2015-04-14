# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def rename_link_type(apps, schema_editor):
    Person2Company = apps.get_model("core", "Person2Company")

    Person2Company.objects.filter(
        relationship_type="Засновник").update(
        relationship_type="Засновник/учасник")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150409_0231'),
    ]

    operations = [
        migrations.RunPython(rename_link_type),
    ]
