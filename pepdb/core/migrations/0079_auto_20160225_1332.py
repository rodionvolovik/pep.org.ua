# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0078_auto_20160224_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='other_recipient',
            field=models.CharField(help_text='\u042f\u043a\u0449\u043e \u043d\u0435 \u0454 PEP\u043e\u043c', max_length=200, verbose_name='\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u0456\u0439', blank=True),
        ),
    ]
