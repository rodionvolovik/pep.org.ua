# coding: utf-8
from __future__ import unicode_literals
from django.contrib import admin
from tasks.models import PersonDeduplication
from django.template.loader import render_to_string


# Register your models here.
class PersonDeduplicationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "person1",
        "person2",
        "timestamp",
        "fuzzy",
        "status"
    )

    list_editable = ("status",)
    list_filter = ("status", "fuzzy")

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


admin.site.register(PersonDeduplication, PersonDeduplicationAdmin)
