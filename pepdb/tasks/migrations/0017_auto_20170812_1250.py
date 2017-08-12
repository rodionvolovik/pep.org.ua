# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0016_beneficiariesmatching'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='beneficiariesmatching',
            options={'verbose_name': '\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u0438 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0439', 'verbose_name_plural': '\u0411\u0435\u043d\u0435\u0444\u0456\u0446\u0456\u0430\u0440\u0438 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0439'},
        ),
        migrations.AddField(
            model_name='beneficiariesmatching',
            name='person_json',
            field=jsonfield.fields.JSONField(null=True, verbose_name='\u0412\u043b\u0430\u0441\u043d\u0438\u043a \u0432 \u0440\u0435\u0454\u0441\u0442\u0440\u0456 PEP'),
        ),
    ]
