# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-04 19:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0058_auto_20180904_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='smidacandidate',
            name='smida_company_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0457'),
        ),
    ]
