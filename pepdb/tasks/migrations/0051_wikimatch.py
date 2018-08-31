# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-30 17:36
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0148_auto_20180826_2045'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0050_auto_20180803_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='\u0421\u0442\u0432\u043e\u0440\u0435\u043d\u043e')),
                ('last_modified', models.DateTimeField(auto_now=True, null=True, verbose_name='\u0417\u043c\u0456\u043d\u0435\u043d\u043e')),
                ('status', models.CharField(choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e'), ('a', '\u0417\u0430\u0441\u0442\u043e\u0441\u043e\u0432\u0430\u043d\u043e'), ('i', '\u0406\u0433\u043d\u043e\u0440\u0443\u0432\u0430\u0442\u0438'), ('r', '\u041f\u043e\u0442\u0440\u0435\u0431\u0443\u0454 \u0434\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u043e\u0457 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u043a\u0438')], db_index=True, default='p', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441')),
                ('pep_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435')),
                ('pep_position', models.TextField(blank=True, null=True, verbose_name='\u041f\u043e\u0441\u0430\u0434\u0430')),
                ('matched_json', django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='\u0417\u043d\u0430\u0439\u0434\u0435\u043d\u043e \u0432 \u0434\u0430\u0442\u0430\u0441\u0435\u0442\u0456')),
                ('name_in_dataset', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u041f\u0406\u0411 \u0437 \u0434\u0430\u0442\u0430\u0441\u0435\u0442\u0443')),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wiki_matches', to='core.Person')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u041a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447')),
            ],
            options={
                'verbose_name': '\u0423\u043d\u0456\u0432\u0435\u0440\u0441\u0430\u043b\u044c\u043d\u0438\u0439 \u043c\u0430\u0442\u0447\u0456\u043d\u0433',
                'verbose_name_plural': '\u0423\u043d\u0456\u0432\u0435\u0440\u0441\u0430\u043b\u044c\u043d\u0456 \u043c\u0430\u0442\u0447\u0456\u043d\u0433\u0438',
            },
        ),
    ]
