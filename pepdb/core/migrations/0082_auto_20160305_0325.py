# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, utils
from core.utils import lookup_term


def fix_terms(apps, schema_editor):
    Ua2EnDictionary = apps.get_model("core", "Ua2EnDictionary")

    def fix(s):
        if s == "<p>None</p>":
            return ""
        return s

    for t in Ua2EnDictionary.objects.all():
        if t.term.lower() != lookup_term(t.term):
            print("'{}': '{}'".format(t.term.lower(), lookup_term(t.term)))

        t.term = lookup_term(t.term)

        try:
            t.save()
        except utils.IntegrityError:
            print(t.term)

    raise Exception


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_auto_20160225_1427'),
    ]

    operations = [
        migrations.RunPython(fix_terms),
    ]
