# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20170125_0155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persondeduplication',
            name='person1',
        ),
        migrations.RemoveField(
            model_name='persondeduplication',
            name='person2',
        ),
        migrations.AddField(
            model_name='persondeduplication',
            name='person1_json',
            field=jsonfield.fields.JSONField(null=True, verbose_name='\u041f\u0435\u0440\u0441\u043e\u043d\u0430 1'),
        ),
        migrations.AddField(
            model_name='persondeduplication',
            name='person2_json',
            field=jsonfield.fields.JSONField(null=True, verbose_name='\u041f\u0435\u0440\u0441\u043e\u043d\u0430 2'),
        ),
        migrations.AddField(
            model_name='persondeduplication',
            name='status',
            field=models.CharField(default='p', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', db_index=True, choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e')]),
        ),
    ]
