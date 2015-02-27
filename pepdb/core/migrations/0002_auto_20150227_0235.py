# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='name_en',
            field=models.CharField(max_length=30, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='name_ua',
            field=models.CharField(max_length=30, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430'),
            preserve_default=True,
        ),
    ]
