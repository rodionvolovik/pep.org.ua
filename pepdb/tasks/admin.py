# coding: utf-8
from __future__ import unicode_literals

import json

from django.contrib import admin
from django.template.loader import render_to_string

from core.models import Declaration
from tasks.models import (
    PersonDeduplication, CompanyMatching, BeneficiariesMatching,
    CompanyDeduplication
)


class PersonDeduplicationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "person1",
        "person2",
        "timestamp",
        "fuzzy",
        "status",
        "applied"
    )

    list_editable = ("status",)
    list_filter = ("status", "fuzzy", "applied")

    ordering = ("timestamp",)

    def _person(self, person):
        return render_to_string(
            "admin/dup_person.jinja",
            {"person": person}
        )

    def person1(self, obj):
        return self._person(obj.person1_json)

    person1.short_description = 'Персона 1'
    person1.allow_tags = True

    def person2(self, obj):
        return self._person(obj.person2_json)
    person2.short_description = 'Персона 2'
    person2.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(PersonDeduplicationAdmin, self).save_model(
            request, obj, form, change)


class CompanyMatchingAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/company_matcher.css",)
        }
        js = ("js/company_matcher.js",)

    list_display = (
        "pk",
        "company",
        "candidates",
        "edrpou_match",
        "status",
    )

    list_filter = ("status",)
    list_editable = ("status", "edrpou_match")
    ordering = ("timestamp",)

    def company(self, obj):
        return render_to_string(
            "admin/company.jinja",
            {"company": obj.company_json}
        )

    company.short_description = 'Компанія PEP'
    company.allow_tags = True

    def candidates(self, obj):
        return render_to_string(
            "admin/company_candidates.jinja",
            {
                "candidates": obj.candidates_json,
                "task_id": obj.pk,
                "edrpou_match": obj.edrpou_match
            }
        )

    candidates.short_description = 'Компанії з реєстру'
    candidates.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(CompanyMatchingAdmin, self).save_model(
            request, obj, form, change)


class BeneficiariesMatchingAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/company_matcher.css",)
        }
        js = ("js/company_matcher.js",)

    list_display = (
        "pk",
        "person_readable",
        "is_family_member",
        "declarations_readable",
        "type_of_connection",
        "pep_company_information_readable",
        "edrpou_match",
        "candidates",
        "status",
    )

    def person_readable(self, obj):
        return render_to_string(
            "admin/dup_person.jinja",
            {"person": obj.person_json}
        )

    person_readable.short_description = 'Персона'
    person_readable.allow_tags = True

    def declarations_readable(self, obj):
        return render_to_string(
            "admin/declarations.jinja",
            {
                "declarations": Declaration.objects.filter(
                    pk__in=obj.declarations)
            }
        )

    declarations_readable.short_description = 'Декларації'
    declarations_readable.allow_tags = True

    list_filter = ("status", "type_of_connection")
    list_editable = ("status", "edrpou_match")
    search_fields = (
        'pep_company_information', 'person_json'
    )

    ordering = ("timestamp",)

    def pep_company_information_readable(self, obj):
        return render_to_string(
            "admin/pep_company.jinja",
            {
                "companies": obj.pep_company_information
            }
        )

    pep_company_information_readable.short_description = "Інформація про компанію з декларацій"
    pep_company_information_readable.allow_tags = True

    def candidates(self, obj):
        return render_to_string(
            "admin/company_candidates.jinja",
            {
                "candidates": obj.candidates_json,
                "task_id": obj.pk,
                "edrpou_match": obj.edrpou_match
            }
        )

    candidates.short_description = 'Компанії з реєстру'
    candidates.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(BeneficiariesMatchingAdmin, self).save_model(
            request, obj, form, change)


class CompanyDeduplicationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "company1",
        "company2",
        "timestamp",
        "fuzzy",
        "status",
        "applied"
    )

    list_editable = ("status",)
    list_filter = ("status", "fuzzy", "applied")

    ordering = ("timestamp",)

    def _company(self, company):
        return render_to_string(
            "admin/dup_company.jinja",
            {"company": company}
        )

    def company1(self, obj):
        return self._company(obj.company1_json)

    company1.short_description = 'Юр. особа 1'
    company1.allow_tags = True

    def company2(self, obj):
        return self._company(obj.company2_json)
    company2.short_description = 'Юр. особа 2'
    company2.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(CompanyDeduplicationAdmin, self).save_model(
            request, obj, form, change)

    def ignore(self, request, queryset):
        queryset.update(status="a")
    ignore.short_description = "Залишити все як є"

    actions = [ignore]


admin.site.register(PersonDeduplication, PersonDeduplicationAdmin)
admin.site.register(CompanyMatching, CompanyMatchingAdmin)
admin.site.register(BeneficiariesMatching, BeneficiariesMatchingAdmin)
admin.site.register(CompanyDeduplication, CompanyDeduplicationAdmin)
