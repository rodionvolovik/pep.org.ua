# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20170301_0207'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companymatching',
            old_name='candidates',
            new_name='candidates_json',
        ),
        migrations.RenameField(
            model_name='companymatching',
            old_name='company',
            new_name='company_json',
        ),
    ]
