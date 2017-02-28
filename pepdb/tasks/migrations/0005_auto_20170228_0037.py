# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20170228_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persondeduplication',
            name='status',
            field=models.CharField(default='p', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', db_index=True, choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e'), ('m', "\u041e\u0431'\u0454\u0434\u043d\u0430\u0442\u0438"), ('a', '\u0417\u0430\u043b\u0438\u0448\u0438\u0442\u0438 \u0432\u0441\u0435 \u044f\u043a \u0454'), ('-', '---------------'), ('d1', '\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u043f\u0435\u0440\u0448\u0443'), ('d2', '\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u0434\u0440\u0443\u0433\u0443')]),
        ),
    ]
