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
        p.wiki_uk = fix(p.wiki_uk)

        p.reputation_assets_uk = fix(p.reputation_assets_uk)
        p.reputation_sanctions_uk = fix(p.reputation_sanctions_uk)
        p.reputation_crimes_uk = fix(p.reputation_crimes_uk)
        p.reputation_manhunt_uk = fix(p.reputation_manhunt_uk)
        p.reputation_convictions_uk = fix(p.reputation_convictions_uk)
        p.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0079_auto_20160225_1332")]

    operations = [migrations.RunPython(fix_markdown_fields)]
