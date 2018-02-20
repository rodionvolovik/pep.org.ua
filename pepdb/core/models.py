# coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry

from core.model.persons import Person
from core.model.companies import Company
from core.model.countries import Country
from core.model.declarations import (
    Declaration, DeclarationExtra, DeclarationToLink, DeclarationToWatch
)
from core.model.translations import Ua2RuDictionary, Ua2EnDictionary
from core.model.connections import (
    Person2Person, Person2Company, Company2Company, Person2Country,
    Company2Country, RelationshipProof
)
from core.model.supplementaries import (
    ActionLog, Document, FeedbackMessage)

__all__ = [
    Person, Company, Country, Declaration, DeclarationExtra,
    Ua2EnDictionary, Ua2RuDictionary, Person2Country, Person2Company,
    Company2Company, Person2Country, Company2Country,
    ActionLog, Document, FeedbackMessage, RelationshipProof,
    DeclarationToLink, DeclarationToWatch
]



@receiver(post_save, sender=LogEntry, dispatch_uid="touch_signal")
def touch_last_modification_time(sender, **kwargs):
    if "instance" not in kwargs:
        return

    if not kwargs.get("created", False):
        return

    instance = kwargs["instance"]
    obj = instance.get_edited_object()

    if isinstance(obj, (Person, Company)):
        obj.last_change = datetime.utcnow()
        obj.last_editor = instance.user
        obj.save()
    elif isinstance(obj, (Person2Person)):
        obj.from_person.last_change = datetime.utcnow()
        obj.from_person.last_editor = instance.user
        obj.from_person.save()
        obj.to_person.last_change = datetime.utcnow()
        obj.to_person.last_editor = instance.user
        obj.to_person.save()
    elif isinstance(obj, (Person2Company)):
        obj.from_person.last_change = datetime.utcnow()
        obj.from_person.last_editor = instance.user
        obj.from_person.save()
        obj.to_company.last_change = datetime.utcnow()
        obj.to_company.last_editor = instance.user
        obj.to_company.save()
    elif isinstance(obj, (Company2Company)):
        obj.from_company.last_change = datetime.utcnow()
        obj.from_company.last_editor = instance.user
        obj.from_company.save()
        obj.to_company.last_change = datetime.utcnow()
        obj.to_company.last_editor = instance.user
        obj.to_company.save()
    elif isinstance(obj, (Company2Country)):
        obj.from_company.last_change = datetime.utcnow()
        obj.from_company.last_editor = instance.user
        obj.from_company.save()
    elif isinstance(obj, (Person2Country)):
        obj.from_person.last_change = datetime.utcnow()
        obj.from_person.last_editor = instance.user
        obj.from_person.save()
