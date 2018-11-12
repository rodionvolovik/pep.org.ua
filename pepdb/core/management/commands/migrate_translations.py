# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
import os.path
from django.conf import settings
from django.db.models import F
from django.core.management.base import BaseCommand, CommandError
from modeltranslation.translator import translator

from core.utils import localized_field


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "from", help="Language to take values from", choices=settings.LANGUAGE_CODES
        )
        parser.add_argument(
            "to", help="Language to store values to", choices=settings.LANGUAGE_CODES
        )

    def handle(self, *args, **options):
        for model in translator.get_registered_models():
            opts = translator.get_options_for_model(model)

            update_clause = {}

            for field in opts.fields:
                update_clause[localized_field(field, options["to"])] = F(
                    localized_field(field, options["from"])
                )

            model.objects.update(**update_clause)
