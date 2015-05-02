# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20150423_0157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='uploader',
            field=models.ForeignKey(related_name='pep_document', verbose_name='\u0425\u0442\u043e \u0437\u0430\u0432\u0430\u043d\u0442\u0430\u0436\u0438\u0432', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
