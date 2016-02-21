# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django_markdown.utils import markdown as _markdown
from django.db import migrations, models


def migrate_markdown_fields(apps, schema_editor):
    Person = apps.get_model("core", "Person")
    Company = apps.get_model("core", "Company")

    for p in Person.objects.all():
        p.wiki_uk = _markdown(p.wiki_uk)
        p.wiki_en = _markdown(p.wiki_en)

        p.reputation_assets_uk = _markdown(p.reputation_assets_uk)
        p.reputation_assets_en = _markdown(p.reputation_assets_en)
        p.reputation_sanctions_uk = _markdown(p.reputation_sanctions_uk)
        p.reputation_sanctions_en = _markdown(p.reputation_sanctions_en)
        p.reputation_crimes_uk = _markdown(p.reputation_crimes_uk)
        p.reputation_crimes_en = _markdown(p.reputation_crimes_en)
        p.reputation_manhunt_uk = _markdown(p.reputation_manhunt_uk)
        p.reputation_manhunt_en = _markdown(p.reputation_manhunt_en)
        p.reputation_convictions_uk = _markdown(p.reputation_convictions_uk)
        p.reputation_convictions_en = _markdown(p.reputation_convictions_en)
        p.save()

    for c in Company.objects.all():
        c.wiki = _markdown(c.wiki)
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_auto_20160213_0335'),
    ]

    operations = [
        migrations.RunPython(migrate_markdown_fields),
    ]
