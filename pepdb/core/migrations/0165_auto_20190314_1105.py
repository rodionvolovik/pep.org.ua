# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-03-14 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0164_auto_20190313_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='declaration',
            name='office',
            field=models.CharField(blank=True, max_length=768, verbose_name='\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='office_en',
            field=models.CharField(blank=True, max_length=768, null=True, verbose_name='\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='office_ru',
            field=models.CharField(blank=True, max_length=768, null=True, verbose_name='\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='office_uk',
            field=models.CharField(blank=True, max_length=768, null=True, verbose_name='\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='position',
            field=models.CharField(blank=True, max_length=768, verbose_name='\u041f\u043e\u0441\u0430\u0434\u0430'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='position_en',
            field=models.CharField(blank=True, max_length=768, null=True, verbose_name='\u041f\u043e\u0441\u0430\u0434\u0430'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='position_ru',
            field=models.CharField(blank=True, max_length=768, null=True, verbose_name='\u041f\u043e\u0441\u0430\u0434\u0430'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='position_uk',
            field=models.CharField(blank=True, max_length=768, null=True, verbose_name='\u041f\u043e\u0441\u0430\u0434\u0430'),
        ),
        migrations.AlterField(
            model_name='declaration',
            name='url',
            field=models.URLField(blank=True, max_length=768, verbose_name='\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f'),
        ),
    ]