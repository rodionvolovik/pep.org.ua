# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from hashlib import sha1

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q

from translitua import translitua

from core.utils import (
    expand_gdrive_download_url, download, title, parse_date,
    get_spreadsheet)
from core.models import Company, Person, Person2Company, Document


class Command(BaseCommand):
    help = ('Loads the GoogleDocs table of PEPs to db')

    def process_company(self, company_id, company_ipn, company_name):
        if not company_ipn and not company_name:
            return None

        if len(company_name) > 250:
            self.stderr.write(
                'Company name {} is too long'.format(company_name))
            return None

        company = None

        for k, v in [("pk", company_id), ("edrpou", company_ipn),
                     ("name", company_name)]:
            try:
                if v:
                    company = Company.objects.get(**{k: v})
                    break
            except Company.DoesNotExist:
                pass

        if company is None:
            company = Company(state_company=True)

        # Set missing params
        if not company.name:
            company.name = company_name

        if not company.edrpou:
            company.edrpou = company_ipn

        company.save()
        return company

    def handle(self, *args, **options):
        peklun = User.objects.get(username="peklun")

        wks = get_spreadsheet().sheet1

        for i, l in enumerate(wks.get_all_records()):
            self.stdout.write(
                'Processing line #{}'.format(i))

            company_ipn = l.get("ІПН", "")
            company_name = l.get("Назва", "")
            person_id = l.get("id персони", "")
            company_id = l.get("id компанії", "")

            person = None
            # First let's search for appropriate company
            company = self.process_company(
                company_id, company_ipn, company_name)

            # No company — no go
            if company is None:
                continue

            # Let's backwrite company id to the spreadsheet for further use
            if company.pk != company_id:
                company_id = company.pk
                wks.update_cell(i + 2, len(l.keys()), company.pk)

            person_name = l.get("ПІБ", "").strip()
            position = l.get("Посада", "").strip()
            person_dob = unicode(l.get("Дата народження", "")).strip()
            person_from = parse_date(l.get("Дата призначення", ""))
            person_to = parse_date(l.get("Дата звільнення", ""))

            doc_received = parse_date(l.get("Дата відповіді", ""))
            doc = l.get("Лінк на відповідь", "").strip()
            website = l.get("лінк на сайт", "").strip()

            # Now let's search for the person
            if person_name:
                # Extra care for initials (especialy those without space)
                person_name = re.sub("\s+", " ",
                                     person_name.replace(".", ". "))

                chunks = person_name.split(" ")

                if len(chunks) == 2:
                    last_name = title(chunks[0])
                    first_name = title(chunks[1])
                elif len(chunks) == 1:
                    continue
                else:
                    last_name = title(" ".join(chunks[:-2]))
                    first_name = title(chunks[-2])
                    patronymic = title(chunks[-1])

                # First we search by person_id (if it's present)
                if person_id:
                    try:
                        person = Person.objects.get(pk=person_id)
                    except Person.DoesNotExist:
                        pass

                # If nothing is found we search for name (for now)
                if not person:
                    try:
                        person = Person.objects.get(
                            first_name__iexact=first_name,
                            last_name__iexact=last_name,
                            patronymic__iexact=patronymic
                        )
                    except Person.MultipleObjectsReturned:
                        self.stderr.write(
                            "Double person {}!".format(person_name))
                    except Person.DoesNotExist:
                        pass

                # If nothing is found, let's create a record for that person
                if not person:
                    person = Person(
                        first_name=first_name,
                        last_name=last_name,
                        patronymic=patronymic
                    )
                    self.stderr.write(
                        "Created new person {}".format(person_name))

                person.is_pep = True
                person.imported = True
                person.type_of_official = 1

                # Parsing date (can be a full date or just a year or
                # year/month)
                if person_dob:
                    person.dob = parse_date(person_dob)
                    if len(person_dob) == 4:
                        person.dob_details = 2  # Only year

                    if len(person_dob) > 4 and len(person_dob) < 7:
                        person.dob_details = 1  # month and year

                person.save()

                if person.pk != person_id:
                    person_id = person.pk
                    wks.update_cell(i + 2, len(l.keys()) - 1, person.pk)

                doc_instance = None
                if doc and "folderview" not in doc \
                        and "drive/#folders" not in doc:
                    doc = expand_gdrive_download_url(doc)
                    doc_hash = sha1(doc).hexdigest()

                    try:
                        doc_instance = Document.objects.get(hash=doc_hash)
                    except Document.DoesNotExist:
                        self.stdout.write(
                            'Downloading file {}'.format(doc))
                        doc_name, doc_san_name, doc_content = download(doc)
                        doc_san_name = translitua(doc_san_name)

                        if doc_name:
                            doc_instance = Document(
                                name_ua=doc_name,
                                uploader=peklun,
                                hash=doc_hash
                            )

                            doc_instance.doc.save(
                                doc_san_name, ContentFile(doc_content))
                            doc_instance.save()

                links = Person2Company.objects.filter(
                    (Q(date_established=person_from) |
                     Q(date_established__isnull=True)),
                    (Q(date_finished=person_to) |
                     Q(date_finished__isnull=True)),
                    from_person=person,
                    to_company=company
                )

                # Delete if there are doubling links
                if len(links) > 1:
                    links.delete()

                link, _ = Person2Company.objects.update_or_create(
                    from_person=person,
                    to_company=company,
                    date_established=person_from,
                    date_finished=person_to
                )

                if not link.relationship_type:
                    link.relationship_type = position

                if doc_instance is not None:
                    link.proof_title = doc_instance.name
                    link.proof = doc_instance.doc.url

                link.date_confirmed = doc_received
                link.is_employee = True

                if not doc and website:
                    link.proof = website

                link.save()
