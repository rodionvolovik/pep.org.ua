# coding: utf-8
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from core.models import (
    Country, Person, Company, Person2Person, Document, Person2Country,
    Person2Company)


class Person2PersonInline(admin.TabularInline):
    model = Person2Person
    fk_name = "from_person"
    extra = 1
    fields = ["from_relationship_type", "to_person", "to_relationship_type",
              "date_established", "date_finished", "proof_title", "proof"]


class Person2PersonBackInline(admin.TabularInline):
    verbose_name = u"Зворотній зв'язок з іншою персоною"
    verbose_name_plural = u"Зворотній зв'язки з іншими персонами"
    model = Person2Person
    fk_name = "to_person"
    extra = 1
    fields = ["from_person", "from_relationship_type", "to_relationship_type",
              "date_established", "date_finished", "proof_title", "proof"]


class Person2CountryInline(admin.TabularInline):
    model = Person2Country
    extra = 1
    fields = ["relationship_type", "to_country", "date_established",
              "date_finished", "proof_title", "proof"]


class Person2CompanyInline(admin.TabularInline):
    model = Person2Company
    extra = 1
    fields = ["relationship_type", "to_company", "date_established",
              "date_finished", "proof_title", "proof"]


class Company2PersonInline(admin.TabularInline):
    model = Person2Company
    fk_name = "to_company"
    extra = 1
    fields = ["relationship_type", "to_company", "date_established",
              "date_finished", "proof_title", "proof"]


class PersonAdmin(admin.ModelAdmin):
    inlines = (Person2PersonInline, Person2PersonBackInline,
               Person2CountryInline, Person2CompanyInline)

    fieldsets = [
        (u"Загальна інформація", {
            'fields': ['last_name', 'first_name', 'patronymic', 'is_pep',
                       'photo', 'dob', 'city_of_birth',
                       'registration']}),

        (u'Додаткова інформація', {
            'fields': ['type_of_official', 'risk_category']}),

        (u'Ділова репутація', {
            'fields': ['reputation_sanctions', 'reputation_crimes',
                       'reputation_manhunt', 'reputation_convictions']}),

        (u'Непублічна інформація', {
            'fields': ['passport_id', 'passport_reg', 'tax_payer_id',
                       'id_number']}),
    ]


class CompanyAdmin(admin.ModelAdmin):
    inlines = (Company2PersonInline, )


class CountryAdmin(TranslationAdmin):
    pass

admin.site.register(Person, PersonAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Document)
