# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_decl_fields(apps, schema_editor):
    Declaration = apps.get_model("core", "Declaration")

    for d in Declaration.objects.all():
        d.office_uk = d.office
        d.position_uk = d.position
        d.region_uk = d.region

        d.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_auto_20160213_0335'),
    ]

    operations = [
        migrations.RunPython(move_decl_fields),
    ]
