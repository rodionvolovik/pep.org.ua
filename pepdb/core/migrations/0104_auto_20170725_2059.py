# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0103_auto_20170724_1702")]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="status",
            field=models.IntegerField(
                default=0,
                verbose_name="\u041f\u043e\u0442\u043e\u0447\u043d\u0438\u0439 \u0441\u0442\u0430\u043d",
                choices=[
                    (
                        0,
                        "\u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f \u0432\u0456\u0434\u0441\u0443\u0442\u043d\u044f",
                    ),
                    (
                        1,
                        "\u0437\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u043e",
                    ),
                    (2, "\u043f\u0440\u0438\u043f\u0438\u043d\u0435\u043d\u043e"),
                    (
                        3,
                        "\u0432 \u0441\u0442\u0430\u043d\u0456 \u043f\u0440\u0438\u043f\u0438\u043d\u0435\u043d\u043d\u044f",
                    ),
                    (
                        4,
                        "\u0437\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u043e, \u0441\u0432\u0456\u0434\u043e\u0446\u0442\u0432\u043e \u043f\u0440\u043e \u0434\u0435\u0440\u0436\u0430\u0432\u043d\u0443 \u0440\u0435\u0454\u0441\u0442\u0440\u0430\u0446\u0456\u044e \u043d\u0435\u0434\u0456\u0439\u0441\u043d\u0435",
                    ),
                    (
                        5,
                        "\u043f\u043e\u0440\u0443\u0448\u0435\u043d\u043e \u0441\u043f\u0440\u0430\u0432\u0443 \u043f\u0440\u043e \u0431\u0430\u043d\u043a\u0440\u0443\u0442\u0441\u0442\u0432\u043e",
                    ),
                    (
                        6,
                        "\u043f\u043e\u0440\u0443\u0448\u0435\u043d\u043e \u0441\u043f\u0440\u0430\u0432\u0443 \u043f\u0440\u043e \u0431\u0430\u043d\u043a\u0440\u0443\u0442\u0441\u0442\u0432\u043e (\u0441\u0430\u043d\u0430\u0446\u0456\u044f)",
                    ),
                ],
            ),
        )
    ]
