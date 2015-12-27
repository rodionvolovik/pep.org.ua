# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_auto_20151224_1930'),
    ]

    operations = [
        migrations.CreateModel(
            name='Declaration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('declaration_id', models.CharField(max_length=50, verbose_name='\u0406\u0434\u0435\u043d\u0442\u0438\u0444\u0456\u043a\u0430\u0442\u043e\u0440', db_index=True)),
                ('last_name', models.CharField(max_length=40, verbose_name='\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435')),
                ('first_name', models.CharField(max_length=40, verbose_name="\u0406\u043c'\u044f")),
                ('patronymic', models.CharField(max_length=40, verbose_name='\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456', blank=True)),
                ('position', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0441\u0430\u0434\u0430', blank=True)),
                ('office', models.CharField(max_length=255, verbose_name='\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e', blank=True)),
                ('region', models.CharField(max_length=50, verbose_name='\u0420\u0435\u0433\u0456\u043e\u043d', blank=True)),
                ('year', models.CharField(max_length=4, verbose_name='\u0420\u0456\u043a', blank=True)),
                ('source', jsonfield.fields.JSONField()),
                ('url', models.URLField(max_length=512, verbose_name='\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f', blank=True)),
                ('confirmed', models.BooleanField(default=False, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e')),
                ('fuzziness', models.IntegerField(default=0, verbose_name='\u0412\u0456\u0434\u0441\u0442\u0430\u043d\u044c')),
                ('person', models.ForeignKey(default=None, to='core.Person')),
            ],
        ),
    ]
