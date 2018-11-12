# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from core.models import Ua2EnDictionary


def move_names(apps, schema_editor):
    Company = apps.get_model("core", "Company")
    en_translations = {}

    for t in Ua2EnDictionary.objects.all():
        en_translations[t.term.lower()] = filter(
            None, [t.translation, t.alt_translation]
        )

    for c in Company.objects.all():
        c.name_ua = c.name
        c.name_en = (en_translations.get(c.name.lower(), [c.name]) or [c.name])[0]

        c.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0041_auto_20151026_0241")]

    operations = [
        migrations.RunPython(move_names, reverse_code=migrations.RunPython.noop)
    ]
