# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20150410_0249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company2company',
            name='proof_title',
            field=models.TextField(help_text='\u041d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434: \u0432\u0438\u043f\u0438\u0441\u043a\u0430 \u0437 \u0440\u0435\u0454\u0441\u0442\u0440\u0443', verbose_name="\u041d\u0430\u0437\u0432\u0430 \u0434\u043e\u043a\u0430\u0437\u0443 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2country',
            name='proof_title',
            field=models.TextField(help_text='\u041d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434: \u0432\u0438\u0442\u044f\u0433', verbose_name="\u041d\u0430\u0437\u0432\u0430 \u0434\u043e\u043a\u0430\u0437\u0443 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2company',
            name='proof',
            field=models.URLField(max_length=250, verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2country',
            name='proof_title',
            field=models.TextField(help_text='\u041d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434: \u043e\u0444\u0456\u0446\u0456\u0439\u043d\u0430 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u044c', verbose_name="\u041d\u0430\u0437\u0432\u0430 \u0434\u043e\u043a\u0430\u0437\u0443 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2person',
            name='proof_title',
            field=models.TextField(help_text='\u041d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434: \u0441\u043a\u043b\u0430\u0434 \u0412\u0420 7-\u0433\u043e \u0441\u043a\u043b\u0438\u043a\u0430\u043d\u043d\u044f', verbose_name="\u041d\u0430\u0437\u0432\u0430 \u0434\u043e\u043a\u0430\u0437\u0443 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True),
            preserve_default=True,
        ),
    ]
