# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0029_auto_20150501_0145")]

    operations = [
        migrations.AddField(
            model_name="person2company",
            name="is_employee",
            field=models.BooleanField(
                default=False,
                verbose_name="\u041f\u0440\u0430\u0446\u044e\u0454(-\u0432\u0430\u0432)",
            ),
            preserve_default=True,
        )
    ]
