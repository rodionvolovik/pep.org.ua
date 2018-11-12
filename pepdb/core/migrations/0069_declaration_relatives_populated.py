# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0068_person2person_declaration")]

    operations = [
        migrations.AddField(
            model_name="declaration",
            name="relatives_populated",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="\u0420\u043e\u0434\u0438\u043d\u0430",
            ),
        )
    ]
