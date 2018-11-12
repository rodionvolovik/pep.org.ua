# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0090_auto_20160727_0211")]

    operations = [
        migrations.AlterField(
            model_name="actionlog",
            name="timestamp",
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name="\u0414\u0430\u0442\u0430 \u0442\u0430 \u0447\u0430\u0441",
            ),
        ),
        migrations.AlterField(
            model_name="declarationextra",
            name="person",
            field=models.ForeignKey(
                related_name="declaration_extras", to="core.Person"
            ),
        ),
    ]
