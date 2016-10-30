# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hashlib import sha1

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q

from translitua import translitua

from core.utils import (
    expand_gdrive_download_url, download, parse_date,
    get_spreadsheet, parse_fullname, mangle_date, lookup_term)

from core.models import (
    Ua2RuDictionary, Company, Person, Person2Company, Document,
    Ua2EnDictionary)


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
                     ("name_uk", company_name)]:
            try:
                if v:
                    company = Company.objects.get(**{k: v})
                    break
            except Company.DoesNotExist:
                pass

        if company is None:
            company = Company(state_company=True)

        # Set missing params
        if not company.name_uk:
            company.name_uk = company_name

        Ua2EnDictionary.objects.get_or_create(term=lookup_term(company_name))

        if not company.edrpou:
            company.edrpou = company_ipn

        company.save()
        return company

    def handle(self, *args, **options):
        peklun = User.objects.get(username="peklun")

        wks = get_spreadsheet().sheet1

        for i, l in enumerate(wks.get_all_records()):
            # reopen it time from time to avoid disconnect by timeout
            if i % 2000 == 0 and i:
                wks = get_spreadsheet().sheet1

            self.stdout.write(
                'Processing line #{}'.format(i))

            company_ipn = l.get("ІПН", "")
            company_name = l.get("Назва", "")
            person_id = l.get("id персони", "")
            company_id = l.get("id компанії", "")
            photo_url = l.get("Фото", "")

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
            docs = l.get("Лінк на відповідь", "").strip()
            website = l.get("лінк на сайт", "").strip()

            # Now let's search for the person
            if person_name:
                last_name, first_name, patronymic = parse_fullname(person_name)

                if not last_name:
                    continue

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
                            first_name_uk__iexact=first_name,
                            last_name_uk__iexact=last_name,
                            patronymic_uk__iexact=patronymic
                        )
                    except Person.MultipleObjectsReturned:
                        self.stderr.write(
                            "Double person {}!".format(person_name))
                    except Person.DoesNotExist:
                        pass

                # If nothing is found, let's create a record for that person
                if not person:
                    person = Person()
                    self.stderr.write(
                        "Created new person {}".format(person_name))

                person.first_name_uk = first_name
                person.last_name_uk = last_name
                person.patronymic_uk = patronymic

                Ua2RuDictionary.objects.get_or_create(term=first_name)
                Ua2RuDictionary.objects.get_or_create(term=last_name)
                Ua2RuDictionary.objects.get_or_create(term=patronymic)

                person.first_name_en = translitua(first_name)
                person.last_name_en = translitua(last_name)
                person.patronymic_en = translitua(patronymic)

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

                # Let's download the photo (if any)
                if not person.photo and photo_url:
                    photo_name, photo_san_name, photo_content = download(
                        photo_url, translitua(person_name))

                    if photo_name:
                        person.photo.save(
                            photo_san_name,
                            ContentFile(photo_content))
                    else:
                        self.stdout.write("Cannot download image %s for %s" % (
                            photo_url, person_name
                        ))

                person.save()

                # Let's write the person id back to the table.
                if person.pk != person_id:
                    person_id = person.pk
                    wks.update_cell(i + 2, len(l.keys()) - 1, person.pk)

                # Now let's download all supporting docs
                docs_downloaded = []
                first_doc_name = False

                # There might be many of them
                for doc in docs.split(", "):
                    doc_instance = None

                    # we cannot download folders from google docs, so let's
                    # skip them

                    if doc and "folderview" not in doc \
                            and "drive/#folders" not in doc:
                        doc = expand_gdrive_download_url(doc)
                        doc_hash = sha1(doc).hexdigest()

                        # Check, if docs
                        try:
                            doc_instance = Document.objects.get(hash=doc_hash)
                        except Document.DoesNotExist:
                            self.stdout.write(
                                'Downloading file {}'.format(doc))
                            doc_name, doc_san_name, doc_content = download(doc)
                            doc_san_name = translitua(doc_san_name)

                            if doc_name:
                                doc_instance = Document(
                                    name_uk=doc_name,
                                    uploader=peklun,
                                    hash=doc_hash
                                )

                                doc_instance.doc.save(
                                    doc_san_name, ContentFile(doc_content))
                                doc_instance.save()
                            else:
                                self.stdout.write(
                                    'Cannot download file {}'.format(doc))

                        if doc_instance:
                            first_doc_name = doc_instance.name_uk
                            docs_downloaded.append(doc_instance.doc.url)

                # Now let's setup links between person and companies
                links = Person2Company.objects.filter(
                    (Q(date_established=person_from) |
                     Q(date_established=mangle_date(person_from)) |
                     Q(date_established__isnull=True)),
                    (Q(date_finished=person_to) |
                     Q(date_finished=mangle_date(person_to)) |
                     Q(date_finished__isnull=True)),
                    from_person=person,
                    to_company=company
                )

                # Delete if there are doubling links
                # including those cases when dates were imported incorrectly
                # because of parse_date
                if len(links) > 1:
                    links.delete()

                link, _ = Person2Company.objects.update_or_create(
                    from_person=person,
                    to_company=company,
                    date_established=person_from,
                    date_established_details=0,
                    date_finished=person_to,
                    date_finished_details=0
                )

                if not link.relationship_type:
                    link.relationship_type = position

                # And translate them
                Ua2EnDictionary.objects.get_or_create(
                    term=lookup_term(position))

                # oh, and add links to supporting docs
                all_docs = docs_downloaded + website.split(", ")
                if all_docs:
                    link.proof = ", ".join(filter(None, all_docs))

                    if first_doc_name:
                        link.proof_title = first_doc_name

                link.date_confirmed = doc_received
                link.is_employee = True

                link.save()
