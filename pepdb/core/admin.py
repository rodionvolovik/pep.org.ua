# coding: utf-8
from __future__ import unicode_literals
import json
from django import forms
from django.contrib import admin
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from grappelli_modeltranslation.admin import (
    TranslationAdmin, TranslationTabularInline)

from core.models import (
    Country, Person, Company, Person2Person, Document, Person2Country,
    Person2Company, Company2Company, Company2Country, Ua2RuDictionary,
    Ua2EnDictionary, FeedbackMessage)


def make_published(modeladmin, request, queryset):
    queryset.update(publish=True)
make_published.short_description = "Опублікувати"


def make_unpublished(modeladmin, request, queryset):
    queryset.update(publish=False)
make_unpublished.short_description = "Приховати"


class Person2PersonInline(admin.TabularInline):
    model = Person2Person
    fk_name = "from_person"
    extra = 1
    fields = ["from_relationship_type", "to_person", "to_relationship_type",
              "date_established", "date_finished", "date_confirmed",
              "proof_title", "proof"]

    raw_id_fields = ('to_person',)
    autocomplete_lookup_fields = {
        'fk': ['to_person'],
    }


class Person2PersonBackInline(admin.TabularInline):
    verbose_name = u"Зворотній зв'язок з іншою персоною"
    verbose_name_plural = u"Зворотні зв'язки з іншими персонами"
    model = Person2Person
    fk_name = "to_person"
    extra = 0
    max_num = 0
    fields = ["from_person", "from_relationship_type", "to_relationship_type",
              "date_established", "date_finished", "date_confirmed",
              "proof_title", "proof"]


class Person2CountryInline(admin.TabularInline):
    model = Person2Country
    extra = 1
    fields = ["relationship_type", "to_country", "date_established",
              "date_finished", "date_confirmed", "proof_title", "proof"]

    raw_id_fields = ('to_country',)
    autocomplete_lookup_fields = {
        'fk': ['to_country'],
    }


class Company2CountryInline(admin.TabularInline):
    model = Company2Country
    extra = 1
    fields = ["relationship_type", "to_country", "date_established",
              "date_finished", "date_confirmed", "proof_title", "proof"]

    raw_id_fields = ('to_country',)
    autocomplete_lookup_fields = {
        'fk': ['to_country'],
    }


class Person2CompanyForm(forms.ModelForm):
    class Meta:
        model = Person2Company
        fields = '__all__'

        widgets = {
            'relationship_type': forms.Textarea(
                attrs={
                    'data-choices': json.dumps(
                        Person2Company._relationships_explained),
                    'class': "suggest"
                })
        }


class Person2CompanyInline(TranslationTabularInline):
    model = Person2Company
    form = Person2CompanyForm
    extra = 1
    fields = ["relationship_type", "is_employee", "to_company",
              "date_established", "date_finished", "date_confirmed",
              "proof_title", "proof"]

    raw_id_fields = ('to_company',)

    autocomplete_lookup_fields = {
        'fk': ['to_company'],
    }

    class Media:
        css = {
            "all": ("css/narrow.css",)
        }
        js = ("js/init_autocompletes.js",)


class Company2PersonInline(admin.TabularInline):
    verbose_name = u"Зв'язок з іншою персоною"
    verbose_name_plural = u"Зв'язки з іншими персонами"

    model = Person2Company
    fk_name = "to_company"
    extra = 1
    fields = ["from_person", "relationship_type", "date_established",
              "date_finished", "date_confirmed", "proof_title", "proof"]

    raw_id_fields = ('from_person',)
    autocomplete_lookup_fields = {
        'fk': ['from_person'],
    }


class Company2CompanyInline(admin.TabularInline):
    model = Company2Company
    fk_name = "from_company"
    extra = 1
    fields = ["relationship_type", "to_company", "date_established",
              "date_finished", "date_confirmed", "equity_part",
              "proof_title", "proof"]

    raw_id_fields = ('to_company',)
    autocomplete_lookup_fields = {
        'fk': ['to_company'],
    }


class Company2CompanyBackInline(admin.TabularInline):
    model = Company2Company
    fk_name = "to_company"
    extra = 0
    max_num = 0
    fields = ["relationship_type", "from_company", "date_established",
              "date_finished", "date_confirmed", "equity_part",
              "proof_title", "proof"]


class PersonAdmin(TranslationAdmin):
    inlines = (Person2PersonInline, Person2PersonBackInline,
               Person2CountryInline, Person2CompanyInline)

    list_display = ("last_name_uk", "first_name_uk", "patronymic_uk",
                    "is_pep", "dob", "type_of_official", "publish")
    readonly_fields = ('names',)
    search_fields = ['last_name_uk', "first_name_uk", "patronymic_uk", "names"]
    actions = [make_published, make_unpublished]

    fieldsets = [
        (u"Загальна інформація", {
            'fields': ['last_name', 'first_name', 'patronymic', 'is_pep',
                       'photo', 'dob', 'dob_details', 'city_of_birth',
                       "publish"]}),

        (u'Додаткова інформація', {
            'fields': ['wiki', 'reputation_assets', 'type_of_official',
                       'risk_category', 'names']}),

        (u'Ділова репутація', {
            'fields': ['reputation_sanctions', 'reputation_crimes',
                       'reputation_manhunt', 'reputation_convictions']}),

        (u'Непублічна інформація', {
            'fields': ['passport_id', 'passport_reg', 'tax_payer_id',
                       'registration', 'id_number']}),
    ]


class CompanyAdmin(TranslationAdmin):
    inlines = (Company2PersonInline, Company2CompanyInline,
               Company2CompanyBackInline, Company2CountryInline)
    list_display = ("name_uk", "edrpou", "state_company", "publish")
    search_fields = ["name_uk", "short_name_uk", "edrpou"]
    actions = [make_published, make_unpublished]


class EmptyValueFilter(admin.SimpleListFilter):
    title = _('Наявність перекладу')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'translation'

    def lookups(self, request, model_admin):
        return (
            ('no', _('Немає')),
            ('yes', _('Є'))
        )

    def queryset(self, request, queryset):
        # to decide how to filter the queryset.
        if self.value() == 'yes':
            return queryset.exclude(
                Q(translation="") | Q(translation__isnull=True))
        if self.value() == 'no':
            return queryset.filter(
                Q(translation="") | Q(translation__isnull=True))


class Ua2RuDictionaryAdmin(admin.ModelAdmin):
    list_display = ("term", "translation", "alt_translation", "comments")
    list_editable = ("translation", "alt_translation", "comments")

    list_filter = (EmptyValueFilter,)


class Ua2EnDictionaryAdmin(admin.ModelAdmin):
    list_display = ("term", "translation", "alt_translation", "comments")
    list_editable = ("translation", "alt_translation", "comments")

    list_filter = (EmptyValueFilter,)


class CountryAdmin(TranslationAdmin):
    list_display = ("name_uk", "name_en", "iso2", "iso3", "is_jurisdiction")


class DocumentAdmin(TranslationAdmin):
    def link(self, obj):
        return '<a href="{0}{1}" target="_blank">Лінк</a>'.format(
            settings.MEDIA_URL, obj.doc)
    link.allow_tags = True
    link.short_description = 'Завантажити'

    list_display = ("name", "link", "uploader", "uploaded")


class FeedbackAdmin(admin.ModelAdmin):
    def link_expanded(self, obj):
        return (u'<a href="{0}" target="_blank">Лінк</a>'.format(obj.link)
                if obj.link else "")

    link_expanded.allow_tags = True
    link_expanded.short_description = 'Джерело'

    def text_expanded(self, obj):
        return (u'<strong><sup>*</sup> {0}</strong>'.format(obj.text)
                if not obj.read else
                u'<span style="font-weight:normal">{0}</span>'.format(
                    obj.text))

    text_expanded.allow_tags = True
    text_expanded.short_description = 'Інформація'

    list_display = ("text_expanded", "person", "link_expanded", "added",
                    "contacts")

    def get_queryset(self, request):
        qs = super(FeedbackAdmin, self).get_queryset(request)
        return qs.order_by("-pk")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        FeedbackMessage.objects.filter(pk=object_id).update(read=True)

        return super(FeedbackAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)


admin.site.register(Person, PersonAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Ua2RuDictionary, Ua2RuDictionaryAdmin)
admin.site.register(Ua2EnDictionary, Ua2EnDictionaryAdmin)
admin.site.register(FeedbackMessage, FeedbackAdmin)
