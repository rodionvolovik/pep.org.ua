# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0092_auto_20160804_1555")]

    operations = [
        migrations.AddField(
            model_name="declaration",
            name="nacp_declaration",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u044f \u041d\u0410\u0417\u041a",
            ),
        )
    ]
