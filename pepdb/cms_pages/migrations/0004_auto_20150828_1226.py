# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [("cms_pages", "0003_auto_20150503_1951")]

    operations = [
        migrations.CreateModel(
            name="ColumnFields",
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
                ("title", models.CharField(max_length=255, blank=True)),
                (
                    "body",
                    wagtail.wagtailcore.fields.RichTextField(
                        verbose_name="\u0422\u0435\u043a\u0441\u0442 \u043a\u043e\u043b\u043e\u043d\u043a\u0438"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="homepage",
            name="body",
            field=wagtail.wagtailcore.fields.RichTextField(
                default="",
                verbose_name="\u0422\u0435\u043a\u0441\u0442 \u043d\u0430 \u0431\u043b\u0430\u043a\u0456\u0442\u043d\u0456\u0439 \u043f\u0430\u043d\u0435\u043b\u0456",
            ),
        ),
        migrations.AlterField(
            model_name="staticpage",
            name="body",
            field=wagtail.wagtailcore.fields.RichTextField(
                verbose_name="\u0422\u0435\u043a\u0441\u0442 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438"
            ),
        ),
        migrations.CreateModel(
            name="HomePageColumn",
            fields=[
                (
                    "columnfields_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="cms_pages.ColumnFields",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(null=True, editable=False, blank=True),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        related_name="columns", to="cms_pages.HomePage"
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
            bases=("cms_pages.columnfields", models.Model),
        ),
    ]
