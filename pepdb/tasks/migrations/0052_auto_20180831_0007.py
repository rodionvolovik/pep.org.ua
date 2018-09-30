# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-30 21:07
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0051_wikimatch'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wikimatch',
            options={'verbose_name': '\u041c\u0430\u0442\u0447\u0456\u043d\u0433 \u0437 WikiData', 'verbose_name_plural': '\u041c\u0430\u0442\u0447\u0456\u043d\u0433\u0438 \u0437 WikiData'},
        ),
        migrations.RemoveField(
            model_name='wikimatch',
            name='name_in_dataset',
        ),
        migrations.AddField(
            model_name='wikimatch',
            name='wikidata_id',
            field=models.CharField(blank=True, max_length=50, verbose_name='\u041a\u043e\u0440\u0435\u043a\u0442\u043d\u0438\u0439 WikiData ID'),
        ),
        migrations.AlterField(
            model_name='wikimatch',
            name='matched_json',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='\u0421\u0443\u0442\u043d\u043e\u0441\u0442\u0456, \u0437\u043d\u0430\u0439\u0434\u0435\u043d\u0456 \u0443 \u0432\u0456\u043a\u0456'),
        ),
    ]
