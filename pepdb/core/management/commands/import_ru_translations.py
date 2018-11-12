# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from core.models import Ua2RuDictionary
from unicodecsv import reader
from django.db.models import F, Func, Value


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_path", help="CSV file to import translations")
        parser.add_argument(
            "--replace",
            default=False,
            action="store_true",
            help="Replace existing non-empty translations",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        successful = 0
        failed = 0

        with open(file_path, "r") as fp:
            r = reader(fp)

            for term, trans in r:
                term = term.strip()
                trans = trans.strip()

                if term and trans:
                    try:
                        obj = Ua2RuDictionary.objects.get(term=term)
                    except Ua2RuDictionary.DoesNotExist:
                        self.stderr.write("Cannot find term %s in db" % term)
                        failed += 1
                        continue
                    except Ua2RuDictionary.MultipleObjectsReturned:
                        self.stderr.write(
                            "More than one result for term %s in db" % term
                        )
                        failed += 1
                        continue

                    # There are translation already
                    if obj.translation:
                        # But it's the same: nothing to do
                        if obj.translation.lower() == trans.lower():
                            continue

                        # If we don't want to overwrite, we'll try to add current translation as
                        # alternative to the existing one
                        if not options["replace"]:
                            # If existing alternative translation differs from our new shiny translation
                            if obj.alt_translation.lower() != trans.lower():
                                # Or more precisely, it's absent
                                if not obj.alt_translation:
                                    # We save it
                                    obj.alt_translation = trans
                                    obj.save()
                                    successful += 1
                                else:
                                    # Otherwise give up
                                    self.stdout.write(
                                        "Not overwritting existing alt_translation %s for term %s with %s"
                                        % (term, obj.alt_translation, trans)
                                    )
                                    failed += 1

                            continue

                    obj.translation = trans
                    obj.save()
                    successful += 1

            self.stdout.write(
                "Import is done, successful: %s, failed: %s" % (successful, failed)
            )
