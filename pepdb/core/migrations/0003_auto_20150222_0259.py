# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import select2.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150222_0250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company2company',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company2company',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='country_of_birth',
            field=select2.fields.ForeignKey(related_name='born_in', verbose_name='\u041a\u0440\u0430\u0457\u043d\u0430 \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f', blank=True, to='core.Country', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='related_persons',
            field=select2.fields.ManyToManyField(to='core.Person', through='core.Person2Person'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2company',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2company',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2person',
            name='date_established',
            field=models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u043f\u043e\u0447\u0430\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person2person',
            name='date_finished',
            field=models.DateField(null=True, verbose_name="\u041a\u043e\u043b\u0438 \u0441\u043a\u0456\u043d\u0447\u0438\u0432\u0441\u044f \u0437\u0432'\u044f\u0437\u043e\u043a", blank=True),
            preserve_default=True,
        ),
    ]
