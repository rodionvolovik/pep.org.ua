# coding: utf-8
from django.contrib import admin

from core.models import Country, Person, Company, Person2Person, Document


class Person2PersonInline(admin.StackedInline):
    model = Person2Person
    fk_name = "from_person"
    extra = 1


class PersonAdmin(admin.ModelAdmin):
    inlines = (Person2PersonInline,)

    fieldsets = [
        (u"Загальна інформація", {
            'fields': ['last_name', 'first_name', 'patronymic', 'is_pep',
                       'photo', 'dob', 'country_of_birth', 'city_of_birth',
                       'registration']}),

        (u'Додаткова інформація', {
            'fields': ['citizenship', 'type_of_official', 'risk_category']}),

        (u'Ділова репутація', {
            'fields': ['reputation_sanctions', 'reputation_crimes',
                       'reputation_manhunt', 'reputation_convictions']}),

        (u'Непублічна інформація', {
            'fields': ['passport_id', 'passport_reg', 'tax_payer_id',
                       'id_number']}),
    ]

admin.site.register(Person, PersonAdmin)
admin.site.register(Company)
admin.site.register(Country)
admin.site.register(Document)
