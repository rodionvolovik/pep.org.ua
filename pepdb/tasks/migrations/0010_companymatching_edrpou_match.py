# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20170301_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='companymatching',
            name='edrpou_match',
            field=models.CharField(max_length=15, null=True, verbose_name='\u0417\u043d\u0430\u0439\u0434\u0435\u043d\u0430 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u044f'),
        ),
    ]
