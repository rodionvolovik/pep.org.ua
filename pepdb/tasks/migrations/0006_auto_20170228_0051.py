# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("tasks", "0005_auto_20170228_0037")]

    operations = [
        migrations.AlterUniqueTogether(
            name="persondeduplication",
            unique_together=set([("person1_id", "person2_id")]),
        )
    ]
