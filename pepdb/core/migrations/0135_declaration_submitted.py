# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-03 23:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0134_auto_20180104_0106'),
    ]

    operations = [
        migrations.AddField(
            model_name='declaration',
            name='submitted',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u044f \u0431\u0443\u043b\u0430 \u043f\u043e\u0434\u0430\u043d\u0430'),
        ),
    ]