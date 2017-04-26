# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_declarations(apps, schema_editor):
    Person2Person = apps.get_model("core", "Person2Person")

    for p2p in Person2Person.objects.all():
        if p2p.declaration_id:
            p2p.declarations = list(
                set(p2p.declarations or []) | set([p2p.declaration_id])
            )

            p2p.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0096_person2person_declarations'),
    ]

    operations = [
        migrations.RunPython(migrate_declarations),
    ]
