# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_wiki(apps, schema_editor):
    Person = apps.get_model("core", "Person")

    for p in Person.objects.all():
        p.wiki_ua = p.wiki

        p.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0047_auto_20151026_1540")]

    operations = [
        migrations.RunPython(move_wiki, reverse_code=migrations.RunPython.noop)
    ]
