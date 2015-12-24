# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_auto_20151224_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ua2endictionary',
            name='term',
            field=models.CharField(unique=True, max_length=512, verbose_name='\u0422\u0435\u0440\u043c\u0456\u043d'),
        ),
        migrations.AlterField(
            model_name='ua2rudictionary',
            name='term',
            field=models.CharField(unique=True, max_length=255, verbose_name='\u0422\u0435\u0440\u043c\u0456\u043d'),
        ),
    ]
