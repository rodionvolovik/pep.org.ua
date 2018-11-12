# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("tasks", "0013_auto_20170302_2353")]

    operations = [
        migrations.AddField(
            model_name="persondeduplication",
            name="applied",
            field=models.BooleanField(default=False, db_index=True),
        )
    ]
