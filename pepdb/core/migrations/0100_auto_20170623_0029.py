# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0099_auto_20170602_2157")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="also_known_as",
            field=models.TextField(
                verbose_name="\u0406\u043d\u0448\u0456 \u0456\u043c\u0435\u043d\u0430",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="also_known_as_en",
            field=models.TextField(
                null=True,
                verbose_name="\u0406\u043d\u0448\u0456 \u0456\u043c\u0435\u043d\u0430",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="also_known_as_uk",
            field=models.TextField(
                null=True,
                verbose_name="\u0406\u043d\u0448\u0456 \u0456\u043c\u0435\u043d\u0430",
                blank=True,
            ),
        ),
    ]
