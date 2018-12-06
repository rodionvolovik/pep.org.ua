# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-30 07:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("tasks", "0047_auto_20180618_0150")]

    operations = [
        migrations.AlterField(
            model_name="terminationnotice",
            name="action",
            field=models.CharField(
                choices=[
                    (
                        "review",
                        "\u041f\u0435\u0440\u0435\u0432\u0456\u0440\u0438\u0442\u0438 \u0432\u0440\u0443\u0447\u043d\u0443",
                    ),
                    (
                        "change_type",
                        "\u0417\u043c\u0456\u043d\u0438\u0442\u0438 \u0442\u0438\u043f \u041f\u0415\u041f \u043d\u0430 \u043f\u043e\u0432'\u044f\u0437\u0430\u043d\u0443 \u043e\u0441\u043e\u0431\u0443",
                    ),
                    (
                        "change_and_fire",
                        "\u0417\u043c\u0456\u043d\u0438\u0442\u0438 \u0442\u0438\u043f \u041f\u0415\u041f \u043d\u0430 \u043f\u043e\u0432'\u044f\u0437\u0430\u043d\u0443 \u043e\u0441\u043e\u0431\u0443 \u0442\u0430 \u0432\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0438 \u0434\u0430\u0442\u0443",
                    ),
                    (
                        "fire",
                        "\u041f\u0440\u0438\u043f\u0438\u043d\u0438\u0442\u0438 \u041f\u0415\u041f\u0441\u0442\u0432\u043e",
                    ),
                    (
                        "fire_related",
                        "\u041f\u0440\u0438\u043f\u0438\u043d\u0438\u0442\u0438 \u041f\u0415\u041f\u0441\u0442\u0432\u043e \u043f\u043e\u0432'\u044f\u0437\u0430\u043d\u043e\u0457 \u043e\u0441\u043e\u0431\u0438",
                    ),
                ],
                db_index=True,
                default="fire",
                max_length=25,
                verbose_name="\u0414\u0456\u044f",
            ),
        )
    ]