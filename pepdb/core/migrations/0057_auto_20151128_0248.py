# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0056_auto_20151128_0206")]

    operations = [
        migrations.AlterField(
            model_name="ua2endictionary",
            name="translation",
            field=models.CharField(
                max_length=512,
                verbose_name="\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0430\u043d\u0433\u043b\u0456\u0439\u0441\u044c\u043a\u043e\u044e",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="ua2rudictionary",
            name="translation",
            field=models.CharField(
                max_length=255,
                verbose_name="\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0434 \u0440\u043e\u0441\u0456\u0439\u0441\u044c\u043a\u043e\u044e",
                blank=True,
            ),
        ),
    ]
