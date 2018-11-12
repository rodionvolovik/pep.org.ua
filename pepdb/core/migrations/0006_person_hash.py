# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0005_auto_20150311_0025")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="hash",
            field=models.CharField(
                max_length=40, verbose_name="\u0425\u0435\u0448", blank=True
            ),
            preserve_default=True,
        )
    ]
