# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0017_auto_20170812_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiariesmatching',
            name='candidates_json',
            field=jsonfield.fields.JSONField(null=True, verbose_name='\u041a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u0438 \u043d\u0430 \u043c\u0430\u0442\u0447\u0456\u043d\u0433'),
        ),
        migrations.AlterField(
            model_name='beneficiariesmatching',
            name='status',
            field=models.CharField(default='p', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', db_index=True, choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e'), ('r', '\u041f\u043e\u0442\u0440\u0435\u0431\u0443\u0454 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u043a\u0438'), ('m', '\u0412\u0438\u043a\u043e\u043d\u0430\u043d\u043e')]),
        ),
        migrations.AlterField(
            model_name='companymatching',
            name='candidates_json',
            field=jsonfield.fields.JSONField(null=True, verbose_name='\u041a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u0438'),
        ),
    ]
