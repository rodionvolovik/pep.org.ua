# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tqdm
from django.core.management.base import BaseCommand
from core.models import Document


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        qs = Document.objects.filter(doc_type_set_manually=False)
        total = qs.count()

        for doc in tqdm.tqdm(qs.nocache().iterator(), total=total):
            doc.guess_doc_type()
