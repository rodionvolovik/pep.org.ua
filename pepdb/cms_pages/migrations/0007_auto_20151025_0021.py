# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [("cms_pages", "0006_auto_20151024_2019")]

    operations = [
        migrations.AddField(
            model_name="columnfields",
            name="body_en",
            field=wagtail.wagtailcore.fields.RichTextField(
                default="",
                verbose_name="[EN] \u0422\u0435\u043a\u0441\u0442 \u043a\u043e\u043b\u043e\u043d\u043a\u0438",
            ),
        ),
        migrations.AddField(
            model_name="columnfields",
            name="title_en",
            field=models.CharField(
                default="",
                max_length=255,
                verbose_name="[EN] \u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
            ),
        ),
        migrations.AddField(
            model_name="homepagebanneritem",
            name="caption_en",
            field=models.CharField(
                max_length=255,
                verbose_name="[EN] \u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="homepagebottommenulink",
            name="caption_en",
            field=models.CharField(
                max_length=255,
                verbose_name="[EN] \u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="homepagetopmenulink",
            name="caption_en",
            field=models.CharField(
                max_length=255,
                verbose_name="[EN] \u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="homepagebanneritem",
            name="caption",
            field=models.CharField(
                max_length=255,
                verbose_name="\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="homepagebottommenulink",
            name="caption",
            field=models.CharField(
                max_length=255,
                verbose_name="\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="homepagetopmenulink",
            name="caption",
            field=models.CharField(
                max_length=255,
                verbose_name="\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a",
                blank=True,
            ),
        ),
    ]
