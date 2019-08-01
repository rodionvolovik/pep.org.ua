# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-01 20:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_auto_20190801_1806'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyCategories',
            fields=[
            ],
            options={
                'verbose_name': '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0456\u0437\u0430\u0446\u0456\u044f \u044e\u0440. \u043e\u0441\u0456\u0431',
                'proxy': True,
                'verbose_name_plural': '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0456\u0437\u0430\u0446\u0456\u044f \u044e\u0440. \u043e\u0441\u0456\u0431',
                'indexes': [],
            },
            bases=('core.company',),
        ),
        migrations.AddField(
            model_name='company',
            name='affiliated_with_pep',
            field=models.BooleanField(default=False, verbose_name="\u041f\u043e\u0432'\u044f\u0437\u0430\u043d\u0430 \u0437 \u043f\u0435\u043f\u043e\u043c"),
        ),
        migrations.AddField(
            model_name='company',
            name='bank',
            field=models.BooleanField(default=False, verbose_name='\u0411\u0430\u043d\u043a'),
        ),
        migrations.AddField(
            model_name='company',
            name='political_party',
            field=models.BooleanField(default=False, verbose_name='\u041f\u043e\u043b\u0456\u0442\u0438\u0447\u043d\u0430 \u043f\u0430\u0440\u0442\u0456\u044f'),
        ),
        migrations.AddField(
            model_name='company',
            name='public_office',
            field=models.BooleanField(default=False, verbose_name='\u0414\u0435\u0440\u0436\u0430\u0432\u043d\u0438\u0439 \u043e\u0440\u0433\u0430\u043d \u0430\u0431\u043e \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0430'),
        ),
        migrations.AddField(
            model_name='company',
            name='service_provider',
            field=models.BooleanField(default=False, verbose_name='\u041f\u0440\u043e\u0444\u0435\u0441\u0456\u0439\u043d\u0438\u0439 \u043d\u0430\u0434\u0430\u0432\u0430\u0447 \u043f\u043e\u0441\u043b\u0443\u0433'),
        ),
        migrations.AddField(
            model_name='company',
            name='state_enterprise',
            field=models.BooleanField(default=False, verbose_name='\u0414\u0435\u0440\u0436\u0430\u0432\u043d\u0430 \u0430\u0431\u043e \u043a\u043e\u043c\u0443\u043d\u0430\u043b\u044c\u043d\u0430 \u0432\u043b\u0430\u0441\u043d\u0456\u0441\u0442\u044c'),
        ),
    ]
