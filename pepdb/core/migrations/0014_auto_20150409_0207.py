# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150326_0331'),
    ]

    operations = [
        migrations.AddField(
            model_name='company2company',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company2company',
            name='equity_part',
            field=models.FloatField(null=True, verbose_name='\u0427\u0430\u0441\u0442\u043a\u0430 \u0432\u043b\u0430\u0441\u043d\u043e\u0441\u0442\u0456 (\u0432\u0456\u0434\u0441\u043e\u0442\u043a\u0438)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company2country',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='dob_details',
            field=models.IntegerField(default=0, verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f: \u0442\u043e\u0447\u043d\u0456\u0441\u0442\u044c', choices=[(0, b'\xd0\xa2\xd0\xbe\xd1\x87\xd0\xbd\xd0\xb0 \xd0\xb4\xd0\xb0\xd1\x82\xd0\xb0'), (1, b'\xd0\xa0\xd1\x96\xd0\xba \xd1\x82\xd0\xb0 \xd0\xbc\xd1\x96\xd1\x81\xd1\x8f\xd1\x86\xd1\x8c'), (2, b'\xd0\xa2\xd1\x96\xd0\xbb\xd1\x8c\xd0\xba\xd0\xb8 \xd1\x80\xd1\x96\xd0\xba')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person2company',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person2country',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person2person',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name="\u0414\u0430\u0442\u0430 \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043d\u044f \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='publish',
            field=models.BooleanField(default=False, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0456\u043a\u0443\u0432\u0430\u0442\u0438'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='publish',
            field=models.BooleanField(default=False, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0456\u043a\u0443\u0432\u0430\u0442\u0438'),
            preserve_default=True,
        ),
    ]
