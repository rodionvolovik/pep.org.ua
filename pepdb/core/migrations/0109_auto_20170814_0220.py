# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-13 23:20
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension



class Migration(migrations.Migration):

    dependencies = [
        ('core', '0108_person2company_declarations'),
    ]

    operations = [
    	TrigramExtension()
    ]
