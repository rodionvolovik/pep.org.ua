# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-30 22:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0121_auto_20170929_1223")]

    operations = [
        migrations.AddField(
            model_name="person2company",
            name="share",
            field=models.DecimalField(
                decimal_places=6,
                max_digits=9,
                null=True,
                verbose_name="\u0420\u043e\u0437\u043c\u0456\u0440 \u0447\u0430\u0441\u0442\u043a\u0438 (\u0432\u0456\u0434\u0441\u043e\u0442\u043a\u0438)",
            ),
        )
    ]
