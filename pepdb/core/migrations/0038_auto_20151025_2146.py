# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from translitua import translitua


def move_names(apps, schema_editor):
    Person = apps.get_model("core", "Person")

    for p in Person.objects.all():
        p.first_name_ua = p.first_name
        p.last_name_ua = p.last_name
        p.patronymic_ua = p.patronymic

        p.first_name_en = translitua(p.first_name)
        p.last_name_en = translitua(p.last_name)
        p.patronymic_en = translitua(p.patronymic)

        p.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0037_auto_20151025_2137")]

    operations = [migrations.RunPython(move_names)]
