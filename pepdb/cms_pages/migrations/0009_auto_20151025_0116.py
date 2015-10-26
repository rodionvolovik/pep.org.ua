# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0008_auto_20151025_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='footer',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] \u0422\u0435\u043a\u0441\u0442 \u0432\u043d\u0438\u0437\u0443 \u0443\u0441\u0456\u0445 \u0441\u0442\u043e\u0440\u0456\u043d\u043e\u043a'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='footer_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u0432\u043d\u0438\u0437\u0443 \u0443\u0441\u0456\u0445 \u0441\u0442\u043e\u0440\u0456\u043d\u043e\u043a'),
        ),
    ]
