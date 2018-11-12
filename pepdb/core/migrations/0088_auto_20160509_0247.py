# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import redactor.fields


class Migration(migrations.Migration):

    dependencies = [("core", "0087_auto_20160419_0250")]

    operations = [
        migrations.CreateModel(
            name="DeclarationExtra",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "date_confirmed",
                    models.DateField(
                        db_index=True,
                        null=True,
                        verbose_name="\u0414\u0430\u0442\u0430",
                        blank=True,
                    ),
                ),
                (
                    "date_confirmed_details",
                    models.IntegerField(
                        default=0,
                        verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
                        choices=[
                            (
                                0,
                                "\u0422\u043e\u0447\u043d\u0430 \u0434\u0430\u0442\u0430",
                            ),
                            (
                                1,
                                "\u0420\u0456\u043a \u0442\u0430 \u043c\u0456\u0441\u044f\u0446\u044c",
                            ),
                            (
                                2,
                                "\u0422\u0456\u043b\u044c\u043a\u0438 \u0440\u0456\u043a",
                            ),
                        ],
                    ),
                ),
                (
                    "section",
                    models.IntegerField(
                        default=0,
                        db_index=True,
                        verbose_name="\u0420\u043e\u0437\u0434\u0456\u043b \u0434\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0457",
                        choices=[
                            (
                                0,
                                "\u0417\u0430\u0433\u0430\u043b\u044c\u043d\u0430 \u0441\u0443\u043c\u0430 \u0441\u0443\u043a\u0443\u043f\u043d\u043e\u0433\u043e \u0434\u043e\u0445\u043e\u0434\u0443, \u0433\u0440\u0438\u0432\u043d\u0456",
                            ),
                            (
                                1,
                                "\u0414\u0430\u0440\u0443\u043d\u043a\u0438, \u043f\u0440\u0438\u0437\u0438, \u0432\u0438\u0433\u0440\u0430\u0448\u0456",
                            ),
                            (
                                2,
                                "\u0417\u0435\u043c\u0435\u043b\u044c\u043d\u0456 \u0434\u0456\u043b\u044f\u043d\u043a\u0438",
                            ),
                            (
                                3,
                                "\u0416\u0438\u0442\u043b\u043e\u0432\u0456 \u0431\u0443\u0434\u0438\u043d\u043a\u0438",
                            ),
                            (4, "\u041a\u0432\u0430\u0440\u0442\u0438\u0440\u0438"),
                            (
                                5,
                                "\u0406\u043d\u0448\u0435 \u043d\u0435\u0440\u0443\u0445\u043e\u043c\u0435 \u043c\u0430\u0439\u043d\u043e",
                            ),
                            (
                                6,
                                "\u0422\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442\u043d\u0456 \u0437\u0430\u0441\u043e\u0431\u0438",
                            ),
                            (
                                7,
                                "\u0412\u043a\u043b\u0430\u0434\u0438 \u0443 \u0431\u0430\u043d\u043a\u0430\u0445",
                            ),
                            (
                                8,
                                "\u0424\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0456 \u0437\u043e\u0431\u043e\u0432\u2019\u044f\u0437\u0430\u043d\u043d\u044f",
                            ),
                            (
                                9,
                                "\u0406\u043d\u0448\u0456 \u0430\u043a\u0442\u0438\u0432\u0438",
                            ),
                        ],
                    ),
                ),
                (
                    "note",
                    redactor.fields.RedactorField(
                        verbose_name="\u0422\u0435\u043a\u0441\u0442"
                    ),
                ),
                (
                    "address",
                    redactor.fields.RedactorField(
                        verbose_name="\u0410\u0434\u0440\u0435\u0441\u0430", blank=True
                    ),
                ),
                ("country", models.ForeignKey(to="core.Country", blank=True)),
                ("person", models.ForeignKey(to="core.Person")),
            ],
            options={
                "verbose_name": "\u0414\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f \u043f\u0440\u043e \u0441\u0442\u0430\u0442\u043a\u0438",
                "verbose_name_plural": "\u0414\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f \u043f\u0440\u043e \u0441\u0442\u0430\u0442\u043a\u0438",
            },
        ),
        migrations.AlterField(
            model_name="company2company",
            name="relationship_type",
            field=models.CharField(
                blank=True,
                max_length=30,
                verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443",
                choices=[
                    (
                        "\u0412\u043b\u0430\u0441\u043d\u0438\u043a",
                        "\u0412\u043b\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u0421\u043f\u0456\u0432\u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                        "\u0421\u043f\u0456\u0432\u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u0421\u043f\u043e\u0440\u0456\u0434\u043d\u0435\u043d\u0430",
                        "\u0421\u043f\u043e\u0440\u0456\u0434\u043d\u0435\u043d\u0430",
                    ),
                    (
                        "\u0417\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a",
                        "\u0417\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a",
                    ),
                    (
                        "\u0421\u043f\u0456\u0432\u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a",
                        "\u0421\u043f\u0456\u0432\u0437\u0430\u0441\u043d\u043e\u0432\u043d\u0438\u043a",
                    ),
                    (
                        "\u041a\u0440\u0435\u0434\u0438\u0442\u043e\u0440 (\u0444\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0438\u0439 \u043f\u0430\u0440\u0442\u043d\u0435\u0440)",
                        "\u041a\u0440\u0435\u0434\u0438\u0442\u043e\u0440 (\u0444\u0456\u043d\u0430\u043d\u0441\u043e\u0432\u0438\u0439 \u043f\u0430\u0440\u0442\u043d\u0435\u0440)",
                    ),
                    (
                        "\u041d\u0430\u0434\u0430\u0432\u0430\u0447 \u043f\u0440\u043e\u0444\u0435\u0441\u0456\u0439\u043d\u0438\u0445 \u043f\u043e\u0441\u043b\u0443\u0433",
                        "\u041d\u0430\u0434\u0430\u0432\u0430\u0447 \u043f\u0440\u043e\u0444\u0435\u0441\u0456\u0439\u043d\u0438\u0445 \u043f\u043e\u0441\u043b\u0443\u0433",
                    ),
                    (
                        "\u041a\u043b\u0456\u0454\u043d\u0442",
                        "\u041a\u043b\u0456\u0454\u043d\u0442",
                    ),
                    (
                        "\u0412\u0438\u043a\u043e\u043d\u0430\u0432\u0435\u0446\u044c",
                        "\u0412\u0438\u043a\u043e\u043d\u0430\u0432\u0435\u0446\u044c",
                    ),
                    (
                        "\u0417\u0430\u043c\u043e\u0432\u043d\u0438\u043a",
                        "\u0417\u0430\u043c\u043e\u0432\u043d\u0438\u043a",
                    ),
                    (
                        "\u041f\u0456\u0434\u0440\u044f\u0434\u043d\u0438\u043a",
                        "\u041f\u0456\u0434\u0440\u044f\u0434\u043d\u0438\u043a",
                    ),
                    (
                        "\u0421\u0443\u0431\u043f\u0456\u0434\u0440\u044f\u0434\u043d\u0438\u043a",
                        "\u0421\u0443\u0431\u043f\u0456\u0434\u0440\u044f\u0434\u043d\u0438\u043a",
                    ),
                    (
                        "\u041f\u043e\u0441\u0442\u0430\u0447\u0430\u043b\u044c\u043d\u0438\u043a",
                        "\u041f\u043e\u0441\u0442\u0430\u0447\u0430\u043b\u044c\u043d\u0438\u043a",
                    ),
                    (
                        "\u041e\u0440\u0435\u043d\u0434\u0430\u0440",
                        "\u041e\u0440\u0435\u043d\u0434\u0430\u0440",
                    ),
                    (
                        "\u041e\u0440\u0435\u043d\u0434\u043e\u0434\u0430\u0432\u0435\u0446\u044c",
                        "\u041e\u0440\u0435\u043d\u0434\u043e\u0434\u0430\u0432\u0435\u0446\u044c",
                    ),
                    (
                        "\u041a\u043e\u043d\u0442\u0440\u0430\u0433\u0435\u043d\u0442",
                        "\u041a\u043e\u043d\u0442\u0440\u0430\u0433\u0435\u043d\u0442",
                    ),
                    (
                        "\u041f\u0440\u0430\u0432\u043e\u043d\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a",
                        "\u041f\u0440\u0430\u0432\u043e\u043d\u0430\u0441\u0442\u0443\u043f\u043d\u0438\u043a",
                    ),
                    (
                        "\u041f\u0440\u0430\u0432\u043e\u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                        "\u041f\u0440\u0430\u0432\u043e\u0432\u043b\u0430\u0441\u043d\u0438\u043a",
                    ),
                    (
                        "\u041c\u0430\u0442\u0435\u0440\u0438\u043d\u0441\u044c\u043a\u0430 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f",
                        "\u041c\u0430\u0442\u0435\u0440\u0438\u043d\u0441\u044c\u043a\u0430 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f",
                    ),
                    (
                        "\u0414\u043e\u0447\u0456\u0440\u043d\u044f \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f",
                        "\u0414\u043e\u0447\u0456\u0440\u043d\u044f \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f",
                    ),
                    (
                        "\u0427\u043b\u0435\u043d \u043d\u0430\u0433\u043b\u044f\u0434\u043e\u0432\u043e\u0433\u043e \u043e\u0440\u0433\u0430\u043d\u0443)",
                        "\u0427\u043b\u0435\u043d \u043d\u0430\u0433\u043b\u044f\u0434\u043e\u0432\u043e\u0433\u043e \u043e\u0440\u0433\u0430\u043d\u0443)",
                    ),
                ],
            ),
        ),
    ]
