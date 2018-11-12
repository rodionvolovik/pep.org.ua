# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0026_auto_20150416_0202")]

    operations = [
        migrations.AlterField(
            model_name="company2company",
            name="proof",
            field=models.TextField(
                verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="company2country",
            name="proof",
            field=models.TextField(
                verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="person2company",
            name="proof",
            field=models.TextField(
                max_length=250,
                verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="person2company",
            name="relationship_type",
            field=models.TextField(
                verbose_name="\u0422\u0438\u043f \u0437\u0432'\u044f\u0437\u043a\u0443",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="person2country",
            name="proof",
            field=models.TextField(
                verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="person2person",
            name="proof",
            field=models.TextField(
                verbose_name="\u041f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
