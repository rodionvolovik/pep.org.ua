# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0015_auto_20170322_0143'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeneficiariesMatching',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='\u0421\u0442\u0432\u043e\u0440\u0435\u043d\u043e')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='\u0417\u043c\u0456\u043d\u0435\u043d\u043e', null=True)),
                ('status', models.CharField(default='p', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', db_index=True, choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e'), ('r', '\u041f\u043e\u0442\u0440\u0435\u0431\u0443\u0454 \u0434\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u043e\u0457 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u043a\u0438'), ('m', '\u0412\u0438\u043a\u043e\u043d\u0430\u043d\u043e')])),
                ('company_key', models.CharField(unique=True, max_length=500, verbose_name='\u041a\u043b\u044e\u0447 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0457')),
                ('person', models.IntegerField(verbose_name='\u0412\u043b\u0430\u0441\u043d\u0438\u043a \u0432 \u0440\u0435\u0454\u0441\u0442\u0440\u0456 PEP')),
                ('is_family_member', models.BooleanField(verbose_name='\u0427\u043b\u0435\u043d \u0440\u043e\u0434\u0438\u043d\u0438')),
                ('declarations', django.contrib.postgres.fields.ArrayField(size=None, base_field=models.IntegerField(), null=True, verbose_name="\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0457, \u0449\u043e \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0443\u044e\u0442\u044c \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True)),
                ('pep_company_information', jsonfield.fields.JSONField(verbose_name='\u0417\u0430\u043f\u0438\u0441\u0438 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0457, \u0437\u0433\u0440\u0443\u043f\u043e\u0432\u0430\u043d\u0456 \u0440\u0430\u0437\u043e\u043c')),
                ('candidates_json', jsonfield.fields.JSONField(null=True, verbose_name='\u041a\u0430\u043d\u0434\u0456\u0434\u0430\u0442\u0438 \u043d\u0430 \u043c\u0430\u0442\u0447\u0456\u043d\u0433')),
                ('edrpou_match', models.CharField(max_length=15, null=True, verbose_name='\u0417\u043d\u0430\u0439\u0434\u0435\u043d\u0430 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f', blank=True)),
                ('user', models.ForeignKey(verbose_name='\u041a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
