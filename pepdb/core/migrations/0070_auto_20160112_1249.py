# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0069_declaration_relatives_populated")]

    operations = [
        migrations.AlterField(
            model_name="declaration",
            name="confirmed",
            field=models.CharField(
                default="p",
                max_length=1,
                verbose_name="\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e",
                db_index=True,
                choices=[
                    (
                        "p",
                        "\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e",
                    ),
                    (
                        "r",
                        "\u041d\u0435 \u043f\u0456\u0434\u0445\u043e\u0434\u0438\u0442\u044c",
                    ),
                    (
                        "a",
                        "\u041e\u043f\u0443\u0431\u043b\u0456\u043a\u043e\u0432\u0430\u043d\u043e",
                    ),
                    (
                        "c",
                        "\u041f\u0435\u0440\u0435\u0432\u0456\u0440\u0438\u0442\u0438",
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="declaration",
            name="relatives_populated",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="\u0420\u043e\u0434\u0438\u043d\u0430 \u0431\u0443\u043b\u0430 \u0432\u043d\u0435\u0441\u0435\u043d\u0430 \u0434\u043e \u0411\u0414",
            ),
        ),
    ]
