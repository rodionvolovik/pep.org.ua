# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0105_auto_20170802_1341'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='legal_entitiy',
            new_name='legal_entity',
        ),
    ]
