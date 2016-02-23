# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('cms_pages', '0010_auto_20160223_0142'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepagebottommenulink',
            name='image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0417\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u043d\u044f', blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AddField(
            model_name='homepagetopmenulink',
            name='image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0417\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u043d\u044f', blank=True, to='wagtailimages.Image', null=True),
        ),
    ]
