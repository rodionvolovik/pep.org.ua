# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0093_declaration_nacp_declaration")]

    operations = [
        migrations.AddField(
            model_name="declaration",
            name="batch_number",
            field=models.IntegerField(
                default=0,
                verbose_name="\u041d\u043e\u043c\u0435\u0440 \u0442\u0435\u043a\u0438",
                db_index=True,
            ),
        )
    ]
