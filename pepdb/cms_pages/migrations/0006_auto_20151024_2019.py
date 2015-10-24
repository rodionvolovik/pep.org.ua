# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0005_auto_20150829_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='body_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u043d\u0430 \u0431\u043b\u0430\u043a\u0438\u0442\u043d\u0456\u0439 \u043f\u0430\u043d\u0435\u043b\u0456'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='title_en',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] \u0422\u0435\u043a\u0441\u0442 \u043d\u0430 \u0431\u043b\u0430\u043a\u0438\u0442\u043d\u0456\u0439 \u043f\u0430\u043d\u0435\u043b\u0456'),
        ),
    ]
