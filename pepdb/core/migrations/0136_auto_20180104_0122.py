# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-03 23:22
from __future__ import unicode_literals

from django.db import migrations
from dateutil.parser import parse as dt_parse


def pull_date_of_submission(apps, schema_editor):
    Declaration = apps.get_model('core.Declaration')

    for d in Declaration.objects.filter(nacp_declaration=True):
        if d.source["intro"].get("date"):
            d.submitted = dt_parse(d.source["intro"]["date"]).date()
            d.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0135_declaration_submitted'),
    ]

    operations = [
        migrations.RunPython(pull_date_of_submission)
    ]
