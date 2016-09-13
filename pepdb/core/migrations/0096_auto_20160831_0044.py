# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_auto_20160831_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationshipproof',
            name='proof_document',
            field=models.ForeignKey(default=None, verbose_name="\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442-\u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", to='core.Document', null=True),
        ),
    ]
