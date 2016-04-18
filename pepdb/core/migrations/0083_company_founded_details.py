# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_auto_20160417_0301'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='founded_details',
            field=models.IntegerField(default=0, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u0442\u0432\u043e\u0440\u0435\u043d\u043d\u044f: \u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c', choices=[(0, '\u0422\u043e\u0447\u043d\u0430 \u0434\u0430\u0442\u0430'), (1, '\u0420\u0456\u043a \u0442\u0430 \u043c\u0456\u0441\u044f\u0446\u044c'), (2, '\u0422\u0456\u043b\u044c\u043a\u0438 \u0440\u0456\u043a')]),
        ),
    ]
