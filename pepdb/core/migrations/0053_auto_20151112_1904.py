# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0052_auto_20151028_1400")]

    operations = [
        migrations.CreateModel(
            name="FeedbackMessage",
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
                    "person",
                    models.CharField(
                        max_length=150,
                        verbose_name="\u041f\u0440\u043e \u043a\u043e\u0433\u043e",
                        blank=True,
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        verbose_name="\u0406\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f"
                    ),
                ),
                (
                    "link",
                    models.URLField(
                        max_length=512,
                        verbose_name="\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f",
                        blank=True,
                    ),
                ),
                (
                    "read",
                    models.BooleanField(
                        default=False,
                        verbose_name="\u041f\u0440\u043e\u0447\u0438\u0442\u0430\u043d\u043e",
                    ),
                ),
                (
                    "added",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="\u0411\u0443\u0432 \u043d\u0430\u0434\u0456\u0441\u043b\u0430\u043d\u0438\u0439",
                    ),
                ),
            ],
            options={
                "verbose_name": "\u0417\u0432\u043e\u0440\u043e\u0442\u043d\u0456\u0439 \u0437\u0432'\u044f\u0437\u043e\u043a",
                "verbose_name_plural": "\u0417\u0432\u043e\u0440\u043e\u0442\u043d\u0456\u0439 \u0437\u0432'\u044f\u0437\u043e\u043a",
            },
        ),
        migrations.AlterField(
            model_name="person",
            name="risk_category",
            field=models.CharField(
                default="low",
                max_length=6,
                verbose_name="\u0420\u0456\u0432\u0435\u043d\u044c \u0440\u0438\u0437\u0438\u043a\u0443",
                choices=[
                    (
                        "danger",
                        "\u041d\u0435\u043f\u0440\u0438\u0439\u043d\u044f\u0442\u043d\u043e \u0432\u0438\u0441\u043e\u043a\u0438\u0439",
                    ),
                    ("high", "\u0412\u0438\u0441\u043e\u043a\u0438\u0439"),
                    ("medium", "\u0421\u0435\u0440\u0435\u0434\u043d\u0456\u0439"),
                    ("low", "\u041d\u0438\u0437\u044c\u043a\u0438\u0439"),
                ],
            ),
        ),
    ]
