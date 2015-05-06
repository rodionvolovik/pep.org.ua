# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_person2company_is_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='reputation_assets',
            field=django_markdown.models.MarkdownField(verbose_name='\u041c\u0430\u0439\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2company',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2company',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u043f\u043e\u0447\u0430\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2company',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2country',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2country',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u043f\u043e\u0447\u0430\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2country',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2company',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2company',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u043f\u043e\u0447\u0430\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2company',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2country',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2country',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u043f\u043e\u0447\u0430\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2country',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2person',
            name='date_confirmed',
            field=models.DateField(null=True, verbose_name='\u041f\u0456\u0434\u0442\u0432\u0435\u0440\u0434\u0436\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2person',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u043f\u043e\u0447\u0430\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2person',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u0417\u0432'\u044f\u0437\u043e\u043a \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f", blank=True),
            preserve_default=True,
        ),
    ]
