# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-23 12:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0116_auto_20170921_1403")]

    operations = [
        migrations.AddField(
            model_name="company",
            name="also_known_as",
            field=models.TextField(
                blank=True,
                verbose_name="\u041d\u0430\u0437\u0432\u0438 \u0456\u043d\u0448\u0438\u043c\u0438 \u043c\u043e\u0432\u0430\u043c\u0438 \u0430\u0431\u043e \u0432\u0430\u0440\u0456\u0430\u0446\u0456\u0457",
            ),
        )
    ]
