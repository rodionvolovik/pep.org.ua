# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tasks", "0007_persondeduplication_fuzzy"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanyMatching",
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
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="\u0421\u0442\u0432\u043e\u0440\u0435\u043d\u043e",
                    ),
                ),
                (
                    "last_modified",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="\u0417\u043c\u0456\u043d\u0435\u043d\u043e",
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default="p",
                        max_length=1,
                        verbose_name="\u0421\u0442\u0430\u0442\u0443\u0441",
                        db_index=True,
                        choices=[
                            (
                                "p",
                                "\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e",
                            ),
                            ("m", "\u0412\u0438\u043a\u043e\u043d\u0430\u043d\u043e"),
                        ],
                    ),
                ),
                (
                    "company",
                    jsonfield.fields.JSONField(
                        null=True,
                        verbose_name="\u041a\u043e\u043c\u043f\u0430\u043d\u0456\u044f",
                    ),
                ),
                (
                    "candidates",
                    jsonfield.fields.JSONField(
                        null=True,
                        verbose_name="\u041a\u0430\u043d\u0434\u0456\u0434\u0430\u0442\u0438",
                    ),
                ),
                ("company_id", models.IntegerField(null=True)),
                (
                    "user",
                    models.ForeignKey(
                        verbose_name="\u041a\u043e\u0440\u0438\u0441\u0442\u0443\u0432\u0430\u0447",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0438 \u043f\u043e\u0448\u0443\u043a\u0443 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0457",
                "verbose_name_plural": "\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0438 \u043f\u043e\u0448\u0443\u043a\u0443 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0439",
            },
        ),
        migrations.AddField(
            model_name="persondeduplication",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True,
                verbose_name="\u0417\u043c\u0456\u043d\u0435\u043d\u043e",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="persondeduplication",
            name="timestamp",
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name="\u0421\u0442\u0432\u043e\u0440\u0435\u043d\u043e",
            ),
        ),
    ]
