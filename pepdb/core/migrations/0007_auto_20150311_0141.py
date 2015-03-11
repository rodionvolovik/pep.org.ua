# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_person_hash'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ua2RuDictionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=255, verbose_name='\u0422\u0435\u0440\u043c\u0456\u043d')),
                ('translation', models.CharField(max_length=255, verbose_name='\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0440\u043e\u0441\u0456\u0439\u0441\u044c\u043a\u043e\u044e')),
                ('alt_translation', models.CharField(max_length=255, verbose_name='\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u0438\u0439 \u043f\u0435\u0440\u0435\u043a\u043b\u0430\u0434', blank=True)),
                ('comments', models.CharField(max_length=100, verbose_name='\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0456', blank=True)),
            ],
            options={
                'verbose_name': '\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0440\u043e\u0441\u0456\u0439\u0441\u044c\u043a\u043e\u044e',
                'verbose_name_plural': '\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434\u0438 \u0440\u043e\u0441\u0456\u0439\u0441\u044c\u043a\u043e\u044e',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='company',
            name='edrpou',
            field=models.CharField(max_length=10, verbose_name='\u0404\u0414\u0420\u041f\u041e\u0423/\u0456\u0434\u0435\u043d\u0442\u0438\u0444\u0456\u043a\u0430\u0446\u0456\u0439\u043d\u0438\u0439 \u043a\u043e\u0434', blank=True),
            preserve_default=True,
        ),
    ]
