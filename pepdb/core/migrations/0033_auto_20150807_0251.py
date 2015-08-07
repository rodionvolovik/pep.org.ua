# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20150725_0347'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='imported',
            field=models.BooleanField(default=False, verbose_name='\u0411\u0443\u0432 \u0456\u043c\u043f\u043e\u0440\u0442\u043e\u0432\u0430\u043d\u0438\u0439 \u0437 \u0433\u0443\u0433\u043b-\u0442\u0430\u0431\u043b\u0438\u0446\u0456'),
        ),
        migrations.AlterField(
            model_name='person',
            name='dob_details',
            field=models.IntegerField(default=0, verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f: \u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c', choices=[(0, '\u0422\u043e\u0447\u043d\u0430 \u0434\u0430\u0442\u0430'), (1, '\u0420\u0456\u043a \u0442\u0430 \u043c\u0456\u0441\u044f\u0446\u044c'), (2, '\u0422\u0456\u043b\u044c\u043a\u0438 \u0440\u0456\u043a')]),
        ),
        migrations.AlterField(
            model_name='person',
            name='type_of_official',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u0422\u0438\u043f \u041f\u0415\u041f', choices=[(1, '\u041d\u0430\u0446\u0456\u043e\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u043f\u0443\u0431\u043b\u0456\u0447\u043d\u0438\u0439 \u0434\u0456\u044f\u0447'), (2, '\u0406\u043d\u043e\u0437\u0435\u043c\u043d\u0438\u0439 \u043f\u0443\u0431\u043b\u0456\u0447\u043d\u0438\u0439 \u0434\u0456\u044f\u0447'), (3, '\u0414\u0456\u044f\u0447, \u0449\u043e \u0432\u0438\u043a\u043e\u043d\u0443\u044e\u0454 \u0437\u043d\u0430\u0447\u043d\u0456 \u0444\u0443\u043d\u043a\u0446\u0456\u0457 \u0432 \u043c\u0456\u0436\u043d\u0430\u0440\u043e\u0434\u043d\u0456\u0439 \u043e\u0440\u0433\u0430\u043d\u0456\u0437\u0430\u0446\u0456\u0457'), (4, "\u041f\u043e\u0432'\u044f\u0437\u0430\u043d\u0430 \u043e\u0441\u043e\u0431\u0430"), (5, '\u0411\u043b\u0438\u0437\u044c\u043a\u0430 \u043e\u0441\u043e\u0431\u0430')]),
        ),
    ]
