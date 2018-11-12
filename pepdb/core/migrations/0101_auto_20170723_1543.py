# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0100_auto_20170623_0029")]

    operations = [
        migrations.AddField(
            model_name="company",
            name="closed_on",
            field=models.DateField(
                null=True,
                verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0440\u0438\u043f\u0438\u043d\u0435\u043d\u043d\u044f",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="closed_on_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0440\u0438\u043f\u0438\u043d\u0435\u043d\u043d\u044f: \u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
                choices=[
                    (0, "\u0422\u043e\u0447\u043d\u0430 \u0434\u0430\u0442\u0430"),
                    (
                        1,
                        "\u0420\u0456\u043a \u0442\u0430 \u043c\u0456\u0441\u044f\u0446\u044c",
                    ),
                    (2, "\u0422\u0456\u043b\u044c\u043a\u0438 \u0440\u0456\u043a"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="legal_entitiy",
            field=models.BooleanField(
                default=True,
                verbose_name="\u0404 \u044e\u0440\u0438\u0434\u0438\u0447\u043d\u043e\u044e \u043e\u0441\u043e\u0431\u043e\u044e",
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="status",
            field=models.IntegerField(
                default=1,
                verbose_name="\u041f\u043e\u0442\u043e\u0447\u043d\u0438\u0439 \u0441\u0442\u0430\u043d",
                choices=[
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
        ),
    ]
