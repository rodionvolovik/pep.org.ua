# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, utils
from core.utils import lookup_term


def fix_terms(apps, schema_editor):
    Ua2EnDictionary = apps.get_model("core", "Ua2EnDictionary")

    for t in Ua2EnDictionary.objects.all():
        t.term = lookup_term(t.term)

        if t.translation:
            duplicates = Ua2EnDictionary.objects.filter(term=t.term).exclude(
                pk=t.pk)
            if duplicates:
                print(t.translation + "::")
                print(";".join(duplicates.values_list("translation", flat=True)))
                print("=" * 30)
                duplicates.delete()

        try:
            t.save()
        except utils.IntegrityError:
            print(t.term, t.translation)
            raise


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_company_founded_details'),
    ]

    operations = [
        migrations.RunPython(fix_terms),
    ]
