# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-12 16:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("tasks", "0028_auto_20180112_1740")]

    operations = [
        migrations.AddField(
            model_name="edrmonitoring",
            name="person_id",
            field=models.IntegerField(null=True),
        )
    ]
