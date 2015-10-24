# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0007_auto_20151025_0021'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticpage',
            name='body_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438'),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='title_en',
            field=models.CharField(default='', max_length=255),
        ),
    ]
