from modeltranslation.translator import translator, TranslationOptions
from core.models import Country, Document


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


class DocumentTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Country, CountryTranslationOptions)
translator.register(Document, DocumentTranslationOptions)
