# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20151026_0244'),
    ]

    operations = [
        migrations.AddField(
            model_name='person2company',
            name='relationship_type_en',
            field=models.TextField(null=True, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
        ),
        migrations.AddField(
            model_name='person2company',
            name='relationship_type_ua',
            field=models.TextField(null=True, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
        ),
    ]
