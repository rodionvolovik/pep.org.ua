# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_auto_20151027_0145'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='name_ua',
            new_name='name_uk',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='short_name_ua',
            new_name='short_name_uk',
        ),
        migrations.RenameField(
            model_name='country',
            old_name='name_ua',
            new_name='name_uk',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='name_ua',
            new_name='name_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='city_of_birth_ua',
            new_name='city_of_birth_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='first_name_ua',
            new_name='first_name_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='last_name_ua',
            new_name='last_name_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='patronymic_ua',
            new_name='patronymic_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='reputation_assets_ua',
            new_name='reputation_assets_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='reputation_convictions_ua',
            new_name='reputation_convictions_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='reputation_crimes_ua',
            new_name='reputation_crimes_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='reputation_manhunt_ua',
            new_name='reputation_manhunt_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='reputation_sanctions_ua',
            new_name='reputation_sanctions_uk',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='wiki_ua',
            new_name='wiki_uk',
        ),
        migrations.RenameField(
            model_name='person2company',
            old_name='relationship_type_ua',
            new_name='relationship_type_uk',
        ),
    ]
