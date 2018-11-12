# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0049_auto_20151027_0132")]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="name",
            field=models.CharField(
                max_length=512,
                verbose_name="\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430",
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="name_en",
            field=models.CharField(
                max_length=512,
                null=True,
                verbose_name="\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430",
            ),
        ),
        migrations.AlterField(
            model_name="company",
            name="name_ua",
            field=models.CharField(
                max_length=512,
                null=True,
                verbose_name="\u041f\u043e\u0432\u043d\u0430 \u043d\u0430\u0437\u0432\u0430",
            ),
        ),
    ]
