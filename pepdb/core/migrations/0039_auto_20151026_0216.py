# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20151025_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ua2EnDictionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=255, verbose_name='\u0422\u0435\u0440\u043c\u0456\u043d')),
                ('translation', models.CharField(max_length=255, verbose_name='\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0430\u043d\u0433\u043b\u0456\u0439\u0441\u044c\u043a\u043e\u044e')),
                ('alt_translation', models.CharField(max_length=255, verbose_name='\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u0438\u0439 \u043f\u0435\u0440\u0435\u043a\u043b\u0430\u0434', blank=True)),
                ('comments', models.CharField(max_length=100, verbose_name='\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0456', blank=True)),
            ],
            options={
                'verbose_name': '\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0430\u043d\u0433\u043b\u0456\u0439\u0441\u044c\u043a\u043e\u044e',
                'verbose_name_plural': '\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434\u0438 \u0430\u043d\u0433\u043b\u0456\u0439\u0441\u044c\u043a\u043e\u044e',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430'),
        ),
        migrations.AddField(
            model_name='company',
            name='name_ua',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430'),
        ),
        migrations.AddField(
            model_name='company',
            name='short_name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0421\u043a\u043e\u0440\u043e\u0447\u0435\u043d\u0430 \u043d\u0430\u0437\u0432\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='short_name_ua',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0421\u043a\u043e\u0440\u043e\u0447\u0435\u043d\u0430 \u043d\u0430\u0437\u0432\u0430', blank=True),
        ),
    ]
