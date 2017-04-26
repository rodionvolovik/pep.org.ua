# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_company_raw_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='person2person',
            name='declarations',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=models.IntegerField(), null=True, verbose_name="\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0457, \u0449\u043e \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0443\u044e\u0442\u044c \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
        ),
    ]
