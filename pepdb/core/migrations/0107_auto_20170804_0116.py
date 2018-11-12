# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0106_auto_20170803_1616")]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="edrpou",
            field=models.CharField(
                max_length=20,
                verbose_name="\u0404\u0414\u0420\u041f\u041e\u0423",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="legal_entity",
            field=models.BooleanField(
                default=True, verbose_name="\u042e\u0440\u043e\u0441\u043e\u0431\u0430"
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="short_name",
            field=models.CharField(
                max_length=100,
                verbose_name="\u0421\u043a\u043e\u0440\u043e\u0447\u0435\u043d\u0430 \u043d\u0430\u0437\u0432\u0430",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="short_name_en",
            field=models.CharField(
                max_length=100,
                null=True,
                verbose_name="\u0421\u043a\u043e\u0440\u043e\u0447\u0435\u043d\u0430 \u043d\u0430\u0437\u0432\u0430",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="short_name_uk",
            field=models.CharField(
                max_length=100,
                null=True,
                verbose_name="\u0421\u043a\u043e\u0440\u043e\u0447\u0435\u043d\u0430 \u043d\u0430\u0437\u0432\u0430",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="state_company",
            field=models.BooleanField(
                default=False,
                verbose_name="\u0414\u0435\u0440\u0436\u0430\u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0430",
            ),
        ),
    ]
