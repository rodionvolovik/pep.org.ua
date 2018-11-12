# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-27 15:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0130_auto_20171129_1645")]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="type_of_official",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (
                        1,
                        "\u041d\u0430\u0446\u0456\u043e\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u043f\u0443\u0431\u043b\u0456\u0447\u043d\u0438\u0439 \u0434\u0456\u044f\u0447",
                    ),
                    (
                        2,
                        "\u0406\u043d\u043e\u0437\u0435\u043c\u043d\u0438\u0439 \u043f\u0443\u0431\u043b\u0456\u0447\u043d\u0438\u0439 \u0434\u0456\u044f\u0447",
                    ),
                    (
                        3,
                        "\u0414\u0456\u044f\u0447, \u0449\u043e \u0432\u0438\u043a\u043e\u043d\u0443\u044e\u0454 \u0437\u043d\u0430\u0447\u043d\u0456 \u0444\u0443\u043d\u043a\u0446\u0456\u0457 \u0432 \u043c\u0456\u0436\u043d\u0430\u0440\u043e\u0434\u043d\u0456\u0439 \u043e\u0440\u0433\u0430\u043d\u0456\u0437\u0430\u0446\u0456\u0457",
                    ),
                    (
                        4,
                        "\u041f\u043e\u0432'\u044f\u0437\u0430\u043d\u0430 \u043e\u0441\u043e\u0431\u0430",
                    ),
                    (5, "\u0427\u043b\u0435\u043d \u0441\u0456\u043c'\u0457"),
                ],
                null=True,
                verbose_name="\u0422\u0438\u043f \u041f\u0415\u041f",
            ),
        )
    ]
