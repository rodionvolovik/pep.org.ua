# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from core.models import Ua2EnDictionary


def move_positions(apps, schema_editor):
    Person2Company = apps.get_model("core", "Person2Company")
    en_translations = {}

    for t in Ua2EnDictionary.objects.all():
        en_translations[t.term.lower()] = filter(None, [
            t.translation, t.alt_translation
        ])

    for p2c in Person2Company.objects.all():
        p2c.relationship_type_ua = p2c.relationship_type

        p2c.relationship_type_en = (en_translations.get(
            p2c.relationship_type.lower(), [p2c.relationship_type]) or
            [p2c.relationship_type])[0]

        p2c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20151026_1131'),
    ]

    operations = [
        migrations.RunPython(
            move_positions, reverse_code=migrations.RunPython.noop),
    ]
