# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [("core", "0046_auto_20151026_1425")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="wiki_en",
            field=django_markdown.models.MarkdownField(
                null=True,
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="wiki_ua",
            field=django_markdown.models.MarkdownField(
                null=True,
                verbose_name="\u0412\u0456\u043a\u0456-\u0441\u0442\u0430\u0442\u0442\u044f",
                blank=True,
            ),
        ),
    ]
