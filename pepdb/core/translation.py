from modeltranslation.translator import translator, TranslationOptions
from core.models import Country


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Country, CountryTranslationOptions)
