# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0084_auto_20160305_0325")]

    operations = [
        migrations.AlterUniqueTogether(
            name="ua2endictionary", unique_together=set([("term", "translation")])
        )
    ]
