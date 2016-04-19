# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def move_dossier(apps, schema_editor):
    Company = apps.get_model("core", "Company")

    for c in Company.objects.all():
        c.city_uk = c.city
        c.street_uk = c.street
        c.appt_uk = c.appt
        c.wiki_uk = c.wiki
        c.other_founders_uk = c.other_founders
        c.other_recipient_uk = c.other_recipient
        c.other_owners_uk = c.other_owners
        c.other_managers_uk = c.other_managers
        c.bank_name_uk = c.bank_name
        c.sanctions_uk = c.sanctions

        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_auto_20160419_0250'),
    ]

    operations = [
        migrations.RunPython(
            move_dossier, reverse_code=migrations.RunPython.noop),
    ]
