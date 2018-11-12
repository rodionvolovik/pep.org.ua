# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0036_auto_20151025_2058")]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="first_name",
            field=models.CharField(max_length=40, verbose_name="\u0406\u043c'\u044f"),
        ),
        migrations.AlterField(
            model_name="person",
            name="first_name_en",
            field=models.CharField(
                max_length=40, null=True, verbose_name="\u0406\u043c'\u044f"
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="first_name_ua",
            field=models.CharField(
                max_length=40, null=True, verbose_name="\u0406\u043c'\u044f"
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_name",
            field=models.CharField(
                max_length=40,
                verbose_name="\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_name_en",
            field=models.CharField(
                max_length=40,
                null=True,
                verbose_name="\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_name_ua",
            field=models.CharField(
                max_length=40,
                null=True,
                verbose_name="\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="patronymic",
            field=models.CharField(
                max_length=40,
                verbose_name="\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="patronymic_en",
            field=models.CharField(
                max_length=40,
                null=True,
                verbose_name="\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="patronymic_ua",
            field=models.CharField(
                max_length=40,
                null=True,
                verbose_name="\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456",
                blank=True,
            ),
        ),
    ]
