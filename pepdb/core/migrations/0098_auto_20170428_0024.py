# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_auto_20170426_2316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='id_number',
        ),
        migrations.RemoveField(
            model_name='person',
            name='passport_id',
        ),
        migrations.RemoveField(
            model_name='person',
            name='passport_reg',
        ),
        migrations.RemoveField(
            model_name='person',
            name='registration',
        ),
        migrations.RemoveField(
            model_name='person',
            name='tax_payer_id',
        ),
    ]
