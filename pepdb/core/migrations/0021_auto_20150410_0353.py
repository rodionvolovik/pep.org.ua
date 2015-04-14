# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20150410_0345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='doc',
            field=models.FileField(upload_to=b'documents', max_length=1000, verbose_name='\u0424\u0430\u0439\u043b'),
            preserve_default=True,
        ),
    ]
