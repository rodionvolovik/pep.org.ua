# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.db import models, migrations


def migrate_proofs(apps, schema_editor):
    # Site = apps.get_model('wagtailcore.Site')
    # Page = apps.get_model('wagtailcore.Page')
    # HomePage = apps.get_model('cms_pages.HomePage')
    content_type_model = apps.get_model('contenttypes.ContentType')

    proof_model = apps.get_model('core.RelationshipProof')
    document_model = apps.get_model('core.Document')

    for model_name in ["Person2Person", "Person2Company", "Person2Country",
                       "Company2Company", "Company2Country"]:
        model = apps.get_model('core.%s' % model_name)

        content_type, _ = content_type_model.objects.get_or_create(
            model=model_name.lower(),
            app_label='core',
            defaults={'name': model_name.lower()}
            if DJANGO_VERSION < (1, 8) else {}
        )

        for obj in model.objects.all():
            for i, p in enumerate(obj.proof.split(", ")):
                p = p.strip()
                if not p:
                    continue

                proof = proof_model(
                    object_id=obj.pk,
                    content_type=content_type,
                )

                if i == 0:
                    proof.proof_title = obj.proof_title

                if p.startswith("http"):
                    proof.proof = p
                else:
                    if p.startswith("/media/"):
                        p = p.replace("/media/", "", 1)

                    try:
                        doc = document_model.objects.get(doc=p)
                        proof.proof_document = doc
                    except document_model.DoesNotExist:
                        if obj._meta.model_name == "person2company":
                            print("%s, %s %s %s, %s" % (
                                obj,
                                obj.from_person.first_name,
                                obj.from_person.patronymic,
                                obj.from_person.last_name,
                                p
                            ))
                        elif obj._meta.model_name == "company2company":
                            print("%s %s %s" % (
                                obj, obj.from_company.name, p))
                        elif obj._meta.model_name == "company2country":
                            print("%s %s %s" % (
                                obj, obj.from_company.name, p))
                        else:
                            print("%s %s %s" % (obj, obj.pk, p))

                proof.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0096_auto_20160831_0044'),
    ]

    operations = [
        migrations.RunPython(migrate_proofs),
    ]
