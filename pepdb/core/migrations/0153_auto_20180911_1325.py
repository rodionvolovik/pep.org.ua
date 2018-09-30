# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-11 10:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0152_auto_20180911_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
        migrations.AlterField(
            model_name='company2company',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
        migrations.AlterField(
            model_name='company2country',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
        migrations.AlterField(
            model_name='person',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
        migrations.AlterField(
            model_name='person2company',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
        migrations.AlterField(
            model_name='person2country',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
        migrations.AlterField(
            model_name='person2person',
            name='_last_modified',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430'),
        ),
    ]
