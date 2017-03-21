# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_persondeduplication_applied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companymatching',
            name='status',
            field=models.CharField(default='p', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', db_index=True, choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e'), ('r', '\u041f\u043e\u0442\u0440\u0435\u0431\u0443\u0454 \u0434\u043e\u0434\u0430\u0442\u043a\u043e\u0432\u043e\u0457 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u043a\u0438'), ('m', '\u0412\u0438\u043a\u043e\u043d\u0430\u043d\u043e')]),
        ),
    ]
