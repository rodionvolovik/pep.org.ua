# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0060_declaration")]

    operations = [
        migrations.AlterField(
            model_name="declaration",
            name="office",
            field=models.CharField(
                max_length=512,
                verbose_name="\u0412\u0456\u0434\u043e\u043c\u0441\u0442\u0432\u043e",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="declaration",
            name="position",
            field=models.CharField(
                max_length=512,
                verbose_name="\u041f\u043e\u0441\u0430\u0434\u0430",
                blank=True,
            ),
        ),
    ]
