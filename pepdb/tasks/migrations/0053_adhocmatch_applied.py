# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-31 20:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0052_auto_20180831_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='adhocmatch',
            name='applied',
            field=models.BooleanField(default=False, verbose_name='\u041c\u0430\u0442\u0447 \u0431\u0443\u043b\u043e \u0437\u0430\u0441\u0442\u043e\u0441\u043e\u0432\u0430\u043d\u043e'),
        ),
    ]
