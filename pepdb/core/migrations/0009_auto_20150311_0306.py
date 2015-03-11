# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150311_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=255, verbose_name='\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430'),
            preserve_default=True,
        ),
    ]
