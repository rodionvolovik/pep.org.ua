# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20170228_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='persondeduplication',
            name='fuzzy',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
