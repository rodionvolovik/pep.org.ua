# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-12-06 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0156_auto_20181206_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='website',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='\u0412\u0435\u0431\u0441\u0430\u0439\u0442'),
        ),
    ]