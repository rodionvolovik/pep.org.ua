# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-03 23:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0133_auto_20180103_2014")]

    operations = [
        migrations.CreateModel(
            name="DeclarationToLink",
            fields=[],
            options={
                "verbose_name": "\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u044f",
                "proxy": True,
                "verbose_name_plural": "\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0457",
                "indexes": [],
            },
            bases=("core.declaration",),
        ),
        migrations.CreateModel(
            name="DeclarationToWatch",
            fields=[],
            options={
                "verbose_name": "\u041c\u043e\u043d\u0456\u0442\u043e\u0440\u0438\u043d\u0433 \u0434\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0439",
                "proxy": True,
                "verbose_name_plural": "\u041c\u043e\u043d\u0456\u0442\u043e\u0440\u0438\u043d\u0433 \u0434\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0439",
                "indexes": [],
            },
            bases=("core.declaration",),
        ),
        migrations.AddField(
            model_name="declaration",
            name="acknowledged",
            field=models.BooleanField(
                db_index=True,
                default=False,
                verbose_name="\u0412\u0456\u0434\u043c\u043e\u043d\u0456\u0442\u043e\u0440\u0435\u043d\u043e",
            ),
        ),
    ]
