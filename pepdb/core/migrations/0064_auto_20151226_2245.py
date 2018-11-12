# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def clear_status(apps, schema_editor):
    m = apps.get_model("core.Declaration")
    m.objects.update(confirmed="p")


class Migration(migrations.Migration):

    dependencies = [("core", "0063_auto_20151226_2241")]

    operations = [migrations.RunPython(clear_status)]
