# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0035_auto_20150830_0300")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="first_name_en",
            field=models.CharField(
                max_length=30, null=True, verbose_name="\u0406\u043c'\u044f"
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="first_name_ua",
            field=models.CharField(
                max_length=30, null=True, verbose_name="\u0406\u043c'\u044f"
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="last_name_en",
            field=models.CharField(
                max_length=30,
                null=True,
                verbose_name="\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="last_name_ua",
            field=models.CharField(
                max_length=30,
                null=True,
                verbose_name="\u041f\u0440\u0456\u0437\u0432\u0438\u0449\u0435",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="patronymic_en",
            field=models.CharField(
                max_length=30,
                null=True,
                verbose_name="\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="patronymic_ua",
            field=models.CharField(
                max_length=30,
                null=True,
                verbose_name="\u041f\u043e-\u0431\u0430\u0442\u044c\u043a\u043e\u0432\u0456",
                blank=True,
            ),
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
