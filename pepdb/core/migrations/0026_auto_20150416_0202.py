# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [("core", "0025_auto_20150416_0124")]

    operations = [
        migrations.AddField(
            model_name="company",
            name="wiki",
            field=django_markdown.models.MarkdownField(
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="person",
            name="wiki",
            field=django_markdown.models.MarkdownField(
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
