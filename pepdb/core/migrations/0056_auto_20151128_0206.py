# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0055_auto_20151115_1810")]

    operations = [
        migrations.AlterField(
            model_name="feedbackmessage",
            name="contacts",
            field=models.TextField(
                max_length=512,
                verbose_name="\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u0438",
                blank=True,
            ),
        )
    ]
