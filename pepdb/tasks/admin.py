# coding: utf-8
from __future__ import unicode_literals
from django.contrib import admin
from tasks.models import PersonDeduplication, CompanyMatching
from django.template.loader import render_to_string


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
        super(PersonDeduplicationAdmin, self).save_model(request, obj, form, change)


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


admin.site.register(PersonDeduplication, PersonDeduplicationAdmin)
admin.site.register(CompanyMatching, CompanyMatchingAdmin)
