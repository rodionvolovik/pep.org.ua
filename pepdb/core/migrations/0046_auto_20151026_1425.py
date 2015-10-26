# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def move_dossier(apps, schema_editor):
    Person = apps.get_model("core", "Person")

    for p in Person.objects.all():
        p.reputation_assets_ua = p.reputation_assets
        p.reputation_sanctions_ua = p.reputation_sanctions
        p.reputation_crimes_ua = p.reputation_crimes
        p.reputation_manhunt_ua = p.reputation_manhunt
        p.reputation_convictions_ua = p.reputation_convictions
        p.city_of_birth_ua = p.city_of_birth

        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20151026_1425'),
    ]

    operations = [
        migrations.RunPython(
            move_dossier, reverse_code=migrations.RunPython.noop),
    ]
