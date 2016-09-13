# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0092_auto_20160804_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelationshipProof',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('proof_title', models.TextField(help_text='\u041d\u0430\u043f\u0440\u0438\u043a\u043b\u0430\u0434: \u0441\u043a\u043b\u0430\u0434 \u0412\u0420 7-\u0433\u043e \u0441\u043a\u043b\u0438\u043a\u0430\u043d\u043d\u044f', verbose_name="\u041d\u0430\u0437\u0432\u0430 \u0434\u043e\u043a\u0430\u0437\u0443 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('proof', models.TextField(verbose_name="\u0430\u0431\u043e \u043f\u043e\u0441\u0438\u043b\u0430\u043d\u043d\u044f \u043d\u0430 \u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('proof_document', models.ForeignKey(verbose_name="\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442-\u0434\u043e\u043a\u0430\u0437 \u0437\u0432'\u044f\u0437\u043a\u0443", to='core.Document')),
            ],
        ),
    ]
