# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_auto_20151229_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='person2person',
            name='declaration',
            field=models.ForeignKey(verbose_name="\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u044f, \u0449\u043e \u043f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0443\u0454 \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True, to='core.Declaration', null=True),
        ),
    ]
