# coding: utf-8
from __future__ import unicode_literals
import json
from django import forms
from django.contrib import admin
from django.db.models import Q
from django.conf import settings
from django.conf.urls import url
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from grappelli_modeltranslation.admin import (
    TranslationAdmin, TranslationTabularInline)

from core.models import (
    Country, Person, Company, Person2Person, Document, Person2Country,
    Person2Company, Company2Company, Company2Country, Ua2RuDictionary,
    Ua2EnDictionary, FeedbackMessage, Declaration)


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
                    "is_pep", "dob", "dob_details", "type_of_official",
                    "publish")
    readonly_fields = ('names',)
    search_fields = ['last_name_uk', "first_name_uk", "patronymic_uk", "names"]
    list_editable = ("dob", "dob_details")

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
    list_display = ("term", "translation", "alt_translation")
    list_editable = ("translation", "alt_translation")

    list_filter = (EmptyValueFilter,)


class Ua2EnDictionaryAdmin(admin.ModelAdmin):
    list_display = ("term", "translation")
    list_editable = ("translation",)

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


def populate_relatives(modeladmin, request, queryset):
    return render(request, "admin/relatives.html", {
        "qs": queryset,
        "referer": request.META.get("HTTP_REFERER"),
        "relations": Person2Person._relationships_explained.keys()
    })

populate_relatives.short_description = "Створити родичів"


class DeclarationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def fullname_decl(self, obj):
        return ('<a href="%s" target="_blank">%s %s %s</a>' % (
            obj.url, obj.last_name, obj.first_name, obj.patronymic)).replace(
            "  ", " ").strip()

    fullname_decl.short_description = 'ПІБ з декларації'
    fullname_decl.admin_order_field = 'last_name'
    fullname_decl.allow_tags = True

    def fullname_pep(self, obj):
        return ("%s %s %s" % (
            obj.person.last_name_uk, obj.person.first_name_uk,
            obj.person.patronymic_uk,
        )).replace("  ", " ").strip()
    fullname_pep.short_description = 'ПІБ з БД PEP'
    fullname_pep.admin_order_field = 'person__last_name_uk'

    def position_decl(self, obj):
        return ("%s @ %s" % (obj.position, obj.office))
    position_decl.short_description = 'Посада з декларації'

    def position_pep(self, obj):
        last_workplace = obj.person.last_workplace
        if last_workplace:
            return "%s @ %s" % (obj.person.last_workplace[1],
                                obj.person.last_workplace[0])

        return ""

    position_pep.short_description = 'Посада з БД PEP'

    def get_urls(self):
        urls = super(DeclarationAdmin, self).get_urls()
        return [
            url(r'^store_relatives/$',
                self.admin_site.admin_view(self.store_relatives),
                name="store_relatives"),
        ] + urls

    def store_relatives(self, request):
        persons_created = 0
        connections_created = 0

        for rec_id in request.POST.getlist('iswear'):
            last_name = request.POST.get("person_%s_last_name" % rec_id)
            first_name = request.POST.get("person_%s_first_name" % rec_id)
            patronymic = request.POST.get("person_%s_patronymic" % rec_id)
            base_person_id = request.POST.get("person_%s_id" % rec_id)
            declaration_id = request.POST.get(
                "person_%s_declaration_id" % rec_id)
            relation_from = request.POST.get(
                "person_%s_relation_from" % rec_id)
            relation_to = request.POST.get(
                "person_%s_relation_to" % rec_id)

            base_person = Person.objects.get(pk=base_person_id)
            declaration = Declaration.objects.get(pk=declaration_id)

            rel_id = request.POST.get("person_%s_rel_id" % rec_id)

            if rel_id:
                relative = Person.objects.get(pk=rel_id)
            else:
                relative = Person.objects.create(
                    first_name_uk=first_name,
                    last_name_uk=last_name,
                    patronymic_uk=patronymic,
                    type_of_official=5,
                    is_pep=False
                )
                persons_created += 1

                # relative, _ = Person.objects.get_or_create(
                #     first_name_uk__iexact=first_name,
                #     last_name_uk__iexact=last_name,
                #     patronymic_uk__iexact=patronymic,
                #     defaults={
                #         "is_pep": False
                #     }
                # )

            _, created = Person2Person.objects.update_or_create(
                from_person=base_person,
                to_person=relative,
                from_relationship_type=relation_from,
                declaration=declaration,
                proof=declaration.url + "?source",
                proof_title=(
                    "Декларація за %s рік" % declaration.year),
                to_relationship_type=relation_to
            )
            if created:
                connections_created += 1

            declaration.relatives_populated = True
            declaration.save()

        self.message_user(
            request, "%s осіб та %s зв'язків було створено." % (
                persons_created, connections_created))

        if request.POST.get("redirect_back"):
            return redirect(request.POST.get("redirect_back"))
        else:
            return redirect(reverse("admin:core_declaration_changelist"))

    def family_table(self, obj):
        family = obj.family
        if family:
            return "".join(
                ["<strong>Родину вже було внесено до БД</strong>"
                 if obj.relatives_populated else ""] +
                ["<table>"] +
                [("<tr><td>{name}</td><td>{relation}</td>" +
                  "<td>{mapped}</td</tr>").format(**x)
                 for x in family if x] +
                ["</table>"])

        return ""

    family_table.short_description = 'Родина'
    family_table.allow_tags = True

    list_select_related = ("person", )

    list_display = (
        "fullname_pep", "fullname_decl", "position_pep", "position_decl",
        "region", "year", "family_table", "confirmed", "fuzziness")

    search_fields = [
        'last_name', "first_name", "patronymic",
        'person__last_name_uk', 'person__first_name_uk',
        'person__patronymic_uk']

    list_editable = ("confirmed",)
    list_filter = ("confirmed", "relatives_populated", )

    actions = [populate_relatives]


admin.site.register(Person, PersonAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Ua2RuDictionary, Ua2RuDictionaryAdmin)
admin.site.register(Ua2EnDictionary, Ua2EnDictionaryAdmin)
admin.site.register(FeedbackMessage, FeedbackAdmin)
admin.site.register(Declaration, DeclarationAdmin)
