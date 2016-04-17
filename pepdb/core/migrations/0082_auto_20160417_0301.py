# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import redactor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_auto_20160225_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='description_en',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='description_uk',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='title',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='title_en',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='title_uk',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='reputation_assets',
            field=redactor.fields.RedactorField(verbose_name='\u0421\u0442\u0430\u0442\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='reputation_assets_en',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0421\u0442\u0430\u0442\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='reputation_assets_uk',
            field=redactor.fields.RedactorField(null=True, verbose_name='\u0421\u0442\u0430\u0442\u043a\u0438', blank=True),
        ),
    ]
