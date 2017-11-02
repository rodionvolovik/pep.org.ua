# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import os.path
import re
from hashlib import sha1
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from translitua import translitua
from core.models import Document


class Command(BaseCommand):
    help = """
    Mass import of documents into db
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'input_dir',
            help='Directory with input files',
        )

    def handle(self, *args, **options):
        peklun = User.objects.get(username="peklun")

        for f in os.listdir(options["input_dir"]):
            if not os.path.isfile(os.path.join(options["input_dir"], f)):
                continue

            fname, ext = os.path.splitext(f)

            human_name = re.sub("[\s_]+", " ", fname.decode("utf-8"))

            doc_san_name = f.decode("utf-8")
            with open(os.path.join(options["input_dir"], f), "rb") as fp:
                doc_content = fp.read()

            doc_hash = sha1(f).hexdigest()

            try:
                doc_instance = Document.objects.get(hash=doc_hash)
                self.stderr.write(
                    'Skipping file {}'.format(doc_san_name))
            except Document.DoesNotExist:
                self.stdout.write(
                    'Adding file {}'.format(doc_san_name))

                if doc_san_name:
                    doc_instance = Document(
                        name_uk=human_name,
                        uploader=peklun,
                        hash=doc_hash
                    )

                    doc_instance.doc.save(
                        doc_san_name, ContentFile(doc_content))
                    doc_instance.save()
