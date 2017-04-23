# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0094_declaration_batch_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='raw_address',
            field=models.TextField(verbose_name='"\u0421\u0438\u0440\u0430" \u0430\u0434\u0440\u0435\u0441\u0430', blank=True),
        ),
    ]
