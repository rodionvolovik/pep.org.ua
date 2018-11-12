# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def fix_markdown_fields(apps, schema_editor):
    Person = apps.get_model("core", "Person")

    def fix(s):
        if s == "<p>None</p>":
            return ""
        return s

    for p in Person.objects.all():
        p.wiki_en = fix(p.wiki_en)

        p.reputation_assets_en = fix(p.reputation_assets_en)
        p.reputation_sanctions_en = fix(p.reputation_sanctions_en)
        p.reputation_crimes_en = fix(p.reputation_crimes_en)
        p.reputation_manhunt_en = fix(p.reputation_manhunt_en)
        p.reputation_convictions_en = fix(p.reputation_convictions_en)
        p.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0077_auto_20160224_0339")]

    operations = [migrations.RunPython(fix_markdown_fields)]
