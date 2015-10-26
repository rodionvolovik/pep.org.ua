from modeltranslation.translator import translator, TranslationOptions
from core.models import Country, Document, Person, Company, Person2Company


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


class DocumentTranslationOptions(TranslationOptions):
    fields = ('name',)


class PersonTranslationOptions(TranslationOptions):
    fields = ('last_name', 'first_name', 'patronymic')


class CompanyTranslationOptions(TranslationOptions):
    fields = ('name', 'short_name')


class Person2CompanyTranslationOptions(TranslationOptions):
    fields = ('relationship_type',)


translator.register(Country, CountryTranslationOptions)
translator.register(Document, DocumentTranslationOptions)
translator.register(Person, PersonTranslationOptions)
translator.register(Company, CompanyTranslationOptions)
translator.register(Person2Company, Person2CompanyTranslationOptions)
