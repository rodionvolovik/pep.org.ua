# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0072_auto_20160210_0246")]

    operations = [
        migrations.AddField(
            model_name="declaration",
            name="office_en",
            field=models.CharField(
                max_length=512,
                null=True,
                verbose_name="\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="declaration",
            name="office_uk",
            field=models.CharField(
                max_length=512,
                null=True,
                verbose_name="\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="declaration",
            name="position_en",
            field=models.CharField(
                max_length=512,
                null=True,
                verbose_name="\u041f\u043e\u0441\u0430\u0434\u0430",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="declaration",
            name="position_uk",
            field=models.CharField(
                max_length=512,
                null=True,
                verbose_name="\u041f\u043e\u0441\u0430\u0434\u0430",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="declaration",
            name="region_en",
            field=models.CharField(
                max_length=50,
                null=True,
                verbose_name="\u0420\u0435\u0433\u0456\u043e\u043d",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="declaration",
            name="region_uk",
            field=models.CharField(
                max_length=50,
                null=True,
                verbose_name="\u0420\u0435\u0433\u0456\u043e\u043d",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="company2company",
            name="date_confirmed_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="company2company",
            name="date_established_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="company2company",
            name="date_finished_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="company2country",
            name="date_confirmed_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="company2country",
            name="date_established_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="company2country",
            name="date_finished_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2company",
            name="date_confirmed_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2company",
            name="date_established_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2company",
            name="date_finished_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2country",
            name="date_confirmed_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2country",
            name="date_established_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2country",
            name="date_finished_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2person",
            name="date_confirmed_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2person",
            name="date_established_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
        migrations.AlterField(
            model_name="person2person",
            name="date_finished_details",
            field=models.IntegerField(
                default=0,
                verbose_name="\u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c",
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
    ]
