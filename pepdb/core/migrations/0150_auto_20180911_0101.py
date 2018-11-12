# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-10 22:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("core", "0149_auto_20180910_1922")]

    operations = [
        migrations.AddField(
            model_name="company",
            name="_last_modified",
            field=models.DateTimeField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AddField(
            model_name="company2company",
            name="_last_modified",
            field=models.DateTimeField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AddField(
            model_name="company2country",
            name="_last_modified",
            field=models.DateTimeField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="_last_modified",
            field=models.DateField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AddField(
            model_name="person2company",
            name="_last_modified",
            field=models.DateTimeField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AddField(
            model_name="person2country",
            name="_last_modified",
            field=models.DateTimeField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AddField(
            model_name="person2person",
            name="_last_modified",
            field=models.DateTimeField(
                null=True,
                verbose_name="\u041e\u0441\u0442\u0430\u043d\u043d\u044f \u0437\u043c\u0456\u043d\u0430",
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="last_change",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="\u0414\u0430\u0442\u0430 \u043e\u0441\u0442\u0430\u043d\u043d\u044c\u043e\u0457 \u0437\u043c\u0456\u043d\u0438 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438 \u043f\u0440\u043e\u0444\u0456\u043b\u044f",
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="last_editor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="\u0410\u0432\u0442\u043e\u0440 \u043e\u0441\u0442\u0430\u043d\u043d\u044c\u043e\u0457 \u0437\u043c\u0456\u043d\u0438 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438 \u043f\u0440\u043e\u0444\u0456\u043b\u044e",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_change",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="\u0414\u0430\u0442\u0430 \u043e\u0441\u0442\u0430\u043d\u043d\u044c\u043e\u0457 \u0437\u043c\u0456\u043d\u0438 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438 \u043f\u0440\u043e\u0444\u0456\u043b\u044f",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_editor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="\u0410\u0432\u0442\u043e\u0440 \u043e\u0441\u0442\u0430\u043d\u043d\u044c\u043e\u0457 \u0437\u043c\u0456\u043d\u0438 \u0441\u0442\u043e\u0440\u0456\u043d\u043a\u0438 \u043f\u0440\u043e\u0444\u0456\u043b\u044e",
            ),
        ),
    ]
