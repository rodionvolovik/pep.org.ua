# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20151026_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='city_of_birth_en',
            field=models.CharField(max_length=100, null=True, verbose_name='\u041c\u0456\u0441\u0442\u043e \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='city_of_birth_ua',
            field=models.CharField(max_length=100, null=True, verbose_name='\u041c\u0456\u0441\u0442\u043e \u043d\u0430\u0440\u043e\u0434\u0436\u0435\u043d\u043d\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_assets_en',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041c\u0430\u0439\u043d\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_assets_ua',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041c\u0430\u0439\u043d\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_convictions_en',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0443\u0434\u0438\u043c\u043e\u0441\u0442\u0456', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_convictions_ua',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0443\u0434\u0438\u043c\u043e\u0441\u0442\u0456', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_crimes_en',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041a\u0440\u0438\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0456 \u0432\u043f\u0440\u043e\u0432\u0430\u0434\u0436\u0435\u043d\u043d\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_crimes_ua',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041a\u0440\u0438\u043c\u0456\u043d\u0430\u043b\u044c\u043d\u0456 \u0432\u043f\u0440\u043e\u0432\u0430\u0434\u0436\u0435\u043d\u043d\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_manhunt_en',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0440\u043e\u0437\u0448\u0443\u043a\u0443', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_manhunt_ua',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041f\u0435\u0440\u0435\u0431\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0440\u043e\u0437\u0448\u0443\u043a\u0443', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_sanctions_en',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0430\u043d\u043a\u0446\u0456\u0439', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='reputation_sanctions_ua',
            field=django_markdown.models.MarkdownField(null=True, verbose_name='\u041d\u0430\u044f\u0432\u043d\u0456\u0441\u0442\u044c \u0441\u0430\u043d\u043a\u0446\u0456\u0439', blank=True),
        ),
    ]
