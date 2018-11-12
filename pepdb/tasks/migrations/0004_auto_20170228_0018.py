# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("tasks", "0003_auto_20170227_2228")]

    operations = [
        migrations.AddField(
            model_name="persondeduplication",
            name="person1_id",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="persondeduplication",
            name="person2_id",
            field=models.IntegerField(null=True),
        ),
    ]
