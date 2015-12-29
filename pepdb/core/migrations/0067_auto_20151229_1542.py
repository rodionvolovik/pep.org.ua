# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_auto_20151227_0205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='declaration',
            name='confirmed',
            field=models.CharField(default='p', max_length=1, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e', db_index=True, choices=[('p', '\u041d\u0435 \u043f\u0435\u0440\u0435\u0432\u0456\u0440\u0435\u043d\u043e'), ('r', '\u041d\u0435 \u043f\u0456\u0434\u0445\u043e\u0434\u0438\u0442\u044c'), ('a', '\u041e\u043f\u0443\u0431\u043b\u0456\u043a\u043e\u0432\u0430\u043d\u043e')]),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='year',
            field=models.CharField(db_index=True, max_length=4, verbose_name='\u0420\u0456\u043a', blank=True),
        ),
        migrations.AlterField(
            model_name='person2country',
            name='relationship_type',
            field=models.CharField(max_length=30, verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443", choices=[('born_in', '\u041d\u0430\u0440\u043e\u0434\u0438\u0432\u0441\u044f(-\u043b\u0430\u0441\u044c)'), ('registered_in', '\u0417\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u0438\u0439(-\u0430)'), ('lived_in', '\u041f\u0440\u043e\u0436\u0438\u0432\u0430\u0432(-\u043b\u0430)'), ('citizenship', '\u0413\u0440\u043e\u043c\u0430\u0434\u044f\u043d\u0438\u043d(-\u043a\u0430)'), ('business', '\u041c\u0430\u0454 \u0437\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u0438\u0439 \u0431\u0456\u0437\u043d\u0435\u0441'), ('realty', '\u041c\u0430\u0454 \u043d\u0435\u0440\u0443\u0445\u043e\u043c\u0456\u0441\u0442\u044c'), ('under_sanctions', '\u041f\u0456\u0434 \u0441\u0430\u043d\u043a\u0446\u0456\u044f\u043c\u0438')]),
        ),
    ]
