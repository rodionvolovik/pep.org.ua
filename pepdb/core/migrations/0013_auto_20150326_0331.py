# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150319_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='founded',
            field=models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043d\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='publish',
            field=models.BooleanField(default=False, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0456\u043a\u043e\u0432\u0430\u0442\u0438'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='short_name',
            field=models.CharField(max_length=50, verbose_name='\u0421\u043a\u043e\u0440\u043e\u0447\u0435\u043d\u0430 \u043d\u0430\u0437\u0432\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='publish',
            field=models.BooleanField(default=False, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0456\u043a\u043e\u0432\u0430\u0442\u0438'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='appt',
            field=models.CharField(max_length=50, verbose_name='\u2116 \u0431\u0443\u0434\u0438\u043d\u043a\u0443, \u043e\u0444\u0456\u0441\u0443', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='city',
            field=models.CharField(max_length=255, verbose_name='\u041c\u0456\u0441\u0442\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='state_company',
            field=models.BooleanField(default=False, verbose_name='\u0404 \u0434\u0435\u0440\u0436\u0430\u0432\u043d\u043e\u044e \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043e\u044e'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='street',
            field=models.CharField(max_length=100, verbose_name='\u0412\u0443\u043b\u0438\u0446\u044f', blank=True),
            preserve_default=True,
        ),
    ]
