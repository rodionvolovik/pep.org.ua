# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20151112_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackmessage',
            name='contacts',
            field=models.URLField(max_length=512, verbose_name='\u0412\u0430\u0448\u0456 \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0438', blank=True),
        ),
    ]
