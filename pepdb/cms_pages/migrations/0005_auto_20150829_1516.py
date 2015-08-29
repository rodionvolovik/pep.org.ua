# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0004_auto_20150828_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='columnfields',
            name='title',
            field=models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043d\u0430 \u0431\u043b\u0430\u043a\u0438\u0442\u043d\u0456\u0439 \u043f\u0430\u043d\u0435\u043b\u0456'),
        ),
        migrations.AlterField(
            model_name='homepagebanneritem',
            name='image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0417\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u043d\u044f', blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AlterField(
            model_name='homepagebanneritem',
            name='link_external',
            field=models.URLField(verbose_name='\u0417\u043e\u0432\u043d\u0456\u0448\u043d\u0454 \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='homepagebanneritem',
            name='link_page',
            field=models.ForeignKey(related_name='+', verbose_name='\u0410\u0431\u043e \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0456\u0441\u043d\u0443\u044e\u0447\u0443 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0443', blank=True, to='wagtailcore.Page', null=True),
        ),
        migrations.AlterField(
            model_name='homepagebottommenulink',
            name='link_external',
            field=models.URLField(verbose_name='\u0417\u043e\u0432\u043d\u0456\u0448\u043d\u0454 \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='homepagebottommenulink',
            name='link_page',
            field=models.ForeignKey(related_name='+', verbose_name='\u0410\u0431\u043e \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0456\u0441\u043d\u0443\u044e\u0447\u0443 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0443', blank=True, to='wagtailcore.Page', null=True),
        ),
        migrations.AlterField(
            model_name='homepagetopmenulink',
            name='link_external',
            field=models.URLField(verbose_name='\u0417\u043e\u0432\u043d\u0456\u0448\u043d\u0454 \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='homepagetopmenulink',
            name='link_page',
            field=models.ForeignKey(related_name='+', verbose_name='\u0410\u0431\u043e \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0456\u0441\u043d\u0443\u044e\u0447\u0443 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0443', blank=True, to='wagtailcore.Page', null=True),
        ),
    ]
