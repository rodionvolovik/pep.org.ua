# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def new_default_status(apps, schema_editor):
    Company = apps.get_model("core", "Company")

    Company.objects.filter(status=1).update(status=0)


class Migration(migrations.Migration):

    dependencies = [("core", "0104_auto_20170725_2059")]

    operations = [migrations.RunPython(new_default_status)]
