# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0098_auto_20170428_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='declaration',
            name='relatives_populated',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u0420\u043e\u0434\u0438\u043d\u0438 \u043d\u0435\u043c\u0430\u0454, \u0430\u0431\u043e \u0432\u0436\u0435 \u0432\u043d\u0435\u0441\u0435\u043d\u0430 \u0434\u043e \u0411\u0414'),
        ),
    ]
