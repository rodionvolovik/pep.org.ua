from modeltranslation.translator import translator, TranslationOptions
from core.models import (
    Country, Document, Person, Company, Person2Company, Declaration)


class CountryTranslationOptions(TranslationOptions):
    fields = ("name",)


class DocumentTranslationOptions(TranslationOptions):
    fields = ("name",)


class PersonTranslationOptions(TranslationOptions):
    fields = ("last_name", "first_name", "patronymic", "wiki", "city_of_birth",
              "reputation_assets", "reputation_sanctions", "reputation_crimes",
              "reputation_manhunt", "reputation_convictions",
              "title", "description", "also_known_as")


class CompanyTranslationOptions(TranslationOptions):
    fields = ("name", "short_name", "city", "street", "appt", "wiki",
              "other_founders", "other_recipient", "other_owners",
              "other_managers", "bank_name", "sanctions")


class Person2CompanyTranslationOptions(TranslationOptions):
    fields = ("relationship_type",)


class DeclarationTranslationOptions(TranslationOptions):
    fields = ("position", "office", "region",)


translator.register(Country, CountryTranslationOptions)
translator.register(Document, DocumentTranslationOptions)
translator.register(Person, PersonTranslationOptions)
translator.register(Company, CompanyTranslationOptions)
translator.register(Person2Company, Person2CompanyTranslationOptions)
translator.register(Declaration, DeclarationTranslationOptions)
