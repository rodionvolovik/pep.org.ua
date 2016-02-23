# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0009_auto_20151025_0116'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='credits',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] \u0422\u0435\u043a\u0441\u0442 \u043f\u0456\u0434 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u043e\u044e'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='credits_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u043f\u0456\u0434 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u043e\u044e'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='subtitle',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] \u0422\u0435\u043a\u0441\u0442 \u043d\u0430\u0434 \u043f\u043e\u0448\u0443\u043a\u043e\u043c'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='subtitle_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u043d\u0430\u0434 \u043f\u043e\u0448\u0443\u043a\u043e\u043c'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] \u0422\u0435\u043a\u0441\u0442 \u043f\u0456\u0434 \u043f\u043e\u0448\u0443\u043a\u043e\u043c'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u043f\u0456\u0434 \u043f\u043e\u0448\u0443\u043a\u043e\u043c'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='footer',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] \u0422\u0435\u043a\u0441\u0442 \u0432\u043d\u0438\u0437\u0443 \u043a\u043e\u0436\u043d\u043e\u0457 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='footer_en',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] \u0422\u0435\u043a\u0441\u0442 \u0432\u043d\u0438\u0437\u0443 \u043a\u043e\u0436\u043d\u043e\u0457 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438'),
        ),
    ]
