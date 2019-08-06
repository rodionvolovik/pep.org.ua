# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-29 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0158_auto_20190513_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='doc_type',
            field=models.CharField(choices=[('business_registry', '\u0412\u0438\u043f\u0438\u0441\u043a\u0438 \u0437 \u0440\u0435\u0454\u0441\u0442\u0440\u0443 \u043a\u043e\u043c\u043f\u0430\u043d\u0456\u0439'), ('court_decision', '\u0420\u0456\u0448\u0435\u043d\u043d\u044f \u0441\u0443\u0434\u0443'), ('declarations', '\u0414\u0435\u043a\u043b\u0430\u0440\u0430\u0446\u0456\u0457'), ('real_estate_registry', '\u0412\u0438\u043f\u0438\u0441\u043a\u0438 \u0437 \u0440\u0435\u0454\u0441\u0442\u0440\u0443 \u043d\u0435\u0440\u0443\u0445\u043e\u043c\u043e\u0441\u0442\u0456'), ('order_to_dismiss', '\u041d\u0430\u043a\u0430\u0437\u0438 \u043f\u0440\u043e \u0437\u0432\u0456\u043b\u044c\u043d\u0435\u043d\u043d\u044f'), ('media', '\u041f\u0443\u0431\u043b\u0456\u043a\u0430\u0446\u0456\u044f \u0432 \u043c\u0435\u0434\u0456\u0430'), ('decree', '\u0420\u0456\u0448\u0435\u043d\u043d\u044f'), ('report', '\u0417\u0432\u0456\u0442\u0438'), ('ownership_structure', '\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0438 \u0432\u043b\u0430\u0441\u043d\u043e\u0441\u0442\u0456'), ('misc', '\u0406\u043d\u0448\u0456 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0438'), ('other', '\u041d\u0435\u043c\u043e\u0436\u043b\u0438\u0432\u043e \u0456\u0434\u0435\u043d\u0442\u0438\u0444\u0456\u043a\u0443\u0432\u0430\u0442\u0438')], default='other', max_length=25, verbose_name='\u0422\u0438\u043f \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0443'),
        ),
    ]