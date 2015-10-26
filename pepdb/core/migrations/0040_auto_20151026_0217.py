# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20151026_0216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ua2endictionary',
            name='alt_translation',
            field=models.CharField(max_length=512, verbose_name='\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u0438\u0439 \u043f\u0435\u0440\u0435\u043a\u043b\u0430\u0434', blank=True),
        ),
        migrations.AlterField(
            model_name='ua2endictionary',
            name='term',
            field=models.CharField(max_length=512, verbose_name='\u0422\u0435\u0440\u043c\u0456\u043d'),
        ),
        migrations.AlterField(
            model_name='ua2endictionary',
            name='translation',
            field=models.CharField(max_length=512, verbose_name='\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0430\u043d\u0433\u043b\u0456\u0439\u0441\u044c\u043a\u043e\u044e'),
        ),
    ]
