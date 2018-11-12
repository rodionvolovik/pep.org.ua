# coding: utf-8
from __future__ import unicode_literals
from datetime import timedelta, datetime, date

from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import formats

from core.models import Declaration, Person2Company
from tasks.models import (
    PersonDeduplication,
    CompanyMatching,
    BeneficiariesMatching,
    CompanyDeduplication,
    EDRMonitoring,
    TerminationNotice,
    AdHocMatch,
    WikiMatch,
    SMIDACandidate,
)


class PersonDeduplicationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "person1",
        "person2",
        "timestamp",
        "fuzzy",
        "status",
        "applied",
    )

    list_editable = ("status",)
    list_filter = ("status", "fuzzy", "applied")

    ordering = ("timestamp",)

    def _person(self, person):
        return render_to_string("admin/dup_person.jinja", {"person": person})

    def person1(self, obj):
        return self._person(obj.person1_json)

    person1.short_description = _("Персона 1")
    person1.allow_tags = True

    def person2(self, obj):
        return self._person(obj.person2_json)

    person2.short_description = _("Персона 2")
    person2.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(PersonDeduplicationAdmin, self).save_model(request, obj, form, change)


class CompanyMatchingAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/company_matcher.css",)}
        js = ("js/company_matcher.js",)

    list_display = ("pk", "company", "candidates", "edrpou_match", "status")

    list_filter = ("status",)
    list_editable = ("status", "edrpou_match")
    ordering = ("timestamp",)

    def company(self, obj):
        return render_to_string("admin/company.jinja", {"company": obj.company_json})

    company.short_description = _("Компанія PEP")
    company.allow_tags = True

    def candidates(self, obj):
        return render_to_string(
            "admin/company_candidates.jinja",
            {
                "candidates": obj.candidates_json,
                "task_id": obj.pk,
                "edrpou_match": obj.edrpou_match,
            },
        )

    candidates.short_description = _("Компанії з реєстру")
    candidates.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(CompanyMatchingAdmin, self).save_model(request, obj, form, change)


class BeneficiariesMatchingAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/company_matcher.css",)}
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
        return render_to_string("admin/dup_person.jinja", {"person": obj.person_json})

    person_readable.short_description = _("Персона")
    person_readable.allow_tags = True

    def declarations_readable(self, obj):
        return render_to_string(
            "admin/declarations.jinja",
            {"declarations": Declaration.objects.filter(pk__in=obj.declarations)},
        )

    declarations_readable.short_description = _("Декларації")
    declarations_readable.allow_tags = True

    list_filter = ("status", "type_of_connection")
    list_editable = ("status", "edrpou_match")
    search_fields = ("pep_company_information", "person_json")

    ordering = ("timestamp",)

    def pep_company_information_readable(self, obj):
        return render_to_string(
            "admin/pep_company.jinja", {"companies": obj.pep_company_information}
        )

    pep_company_information_readable.short_description = _(
        "Інформація про компанію з декларацій"
    )
    pep_company_information_readable.allow_tags = True

    def candidates(self, obj):
        return render_to_string(
            "admin/company_candidates.jinja",
            {
                "candidates": obj.candidates_json,
                "task_id": obj.pk,
                "edrpou_match": obj.edrpou_match,
            },
        )

    candidates.short_description = _("Компанії з реєстру")
    candidates.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(BeneficiariesMatchingAdmin, self).save_model(request, obj, form, change)


class CompanyDeduplicationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "company1",
        "company2",
        "timestamp",
        "fuzzy",
        "status",
        "applied",
    )

    list_editable = ("status",)
    list_filter = ("status", "fuzzy", "applied")

    ordering = ("timestamp",)

    def _company(self, company):
        return render_to_string("admin/dup_company.jinja", {"company": company})

    def company1(self, obj):
        return self._company(obj.company1_json)

    company1.short_description = _("Юр. особа 1")
    company1.allow_tags = True

    def company2(self, obj):
        return self._company(obj.company2_json)

    company2.short_description = _("Юр. особа 2")
    company2.allow_tags = True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(CompanyDeduplicationAdmin, self).save_model(request, obj, form, change)

    def ignore(self, request, queryset):
        queryset.update(status="a")

    ignore.short_description = _("Залишити все як є")

    actions = [ignore]


class EDRMonitoringAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "pep_name_readable",
        "edr_name",
        "pep_position_readable",
        "company_readable",
        "edr_date",
        "name_match_score",
        "applied",
        "status",
    )

    list_editable = ("status", "applied")
    list_filter = ("status", "applied")

    ordering = ("timestamp",)
    search_fields = ("pep_name", "edr_name", "pep_position", "company_edrpou")

    def mark_for_application(self, request, queryset):
        queryset.update(status="a")

    mark_for_application.short_description = _("Статус: Застосувати зміну")

    def ignore(self, request, queryset):
        queryset.update(status="i")

    ignore.short_description = _("Статус: Ігнорувати зміну")

    def doublecheck(self, request, queryset):
        queryset.update(status="r")

    doublecheck.short_description = _("Статус: Потребує додаткової перевірки")

    def apply_manually(self, request, queryset):
        queryset.update(applied=True)

    apply_manually.short_description = _("Було застосовано вручну")

    actions = [mark_for_application, ignore, doublecheck, apply_manually]

    def pep_name_readable(self, obj):
        return '<a href="{}" target="_blank">{}</a>'.format(
            reverse("person_details", kwargs={"person_id": obj.person_id}), obj.pep_name
        )

    pep_name_readable.short_description = _("Прізвище керівника з БД ПЕП")
    pep_name_readable.allow_tags = True
    pep_name_readable.admin_order_field = "pep_name"

    def pep_position_readable(self, obj):
        try:
            p2c = Person2Company.objects.get(pk=obj.relation_id)

            if p2c.date_established or p2c.date_finished:
                return "{}<br/> ({}—{})".format(
                    obj.pep_position,
                    p2c.date_established_human,
                    p2c.date_finished_human,
                )
        except Person2Company.DoesNotExist:
            pass
        return obj.pep_position

    pep_position_readable.short_description = _("Посада ПЕП")
    pep_position_readable.allow_tags = True
    pep_position_readable.admin_order_field = "pep_position"

    def company_readable(self, obj):
        edrpou = unicode(obj.company_edrpou).rjust(8, "0")

        return (
            '<a href="{}" target="_blank">{}</a> '
            + '(<a href="https://ring.org.ua/edr/uk/company/{}" target="_blank">{}</a>)'
        ).format(
            reverse("company_details", kwargs={"company_id": obj.company_id}),
            obj.pep_company_json["name_uk"],
            edrpou,
            edrpou,
        )

    company_readable.short_description = _("Компанія де ПЕП є керівником")
    company_readable.allow_tags = True
    company_readable.admin_order_field = "company_edrpou"

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(EDRMonitoringAdmin, self).save_model(request, obj, form, change)


class TerminationNoticeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "comments",
        "termination_date_ceiled_readable",
        "pep_name_readable",
        "pep_position_readable",
        "new_person_status",
        "action",
        "applied",
        "status",
    )

    list_editable = ("status",)
    list_filter = ("status", "action", "new_person_status", "applied")

    ordering = ("termination_date_ceiled",)

    search_fields = ("pep_name", "pep_position", "comments")

    def termination_date_ceiled_readable(self, obj):
        if obj.termination_date_ceiled is None:
            return "-"

        dt = formats.date_format(obj.termination_date_ceiled, "SHORT_DATE_FORMAT")

        if obj.termination_date_ceiled + timedelta(days=3 * 365) < date.today():
            return _("<strong>{}</strong><br/>Три роки пройшло").format(dt)
        else:
            return dt

    termination_date_ceiled_readable.short_description = _(
        "Дата припинення (округлена вгору)"
    )
    termination_date_ceiled_readable.allow_tags = True
    termination_date_ceiled_readable.admin_order_field = "termination_date_ceiled"

    def pep_name_readable(self, obj):
        if obj.person:
            return '<a href="{}" target="_blank">{}</a>'.format(
                obj.person.get_absolute_url(), obj.pep_name
            )
        else:
            return obj.pep_name

    pep_name_readable.short_description = _("Прізвище керівника з БД ПЕП")
    pep_name_readable.allow_tags = True
    pep_name_readable.admin_order_field = "pep_name"

    def pep_position_readable(self, obj):
        res = obj.pep_position
        if not obj.person:
            return res

        pd = obj.person._last_workplace_from_declaration()
        if pd:
            res += _(
                '<br/><br/> Декларація за {}: <a href="{}" target="blank">{} @ {}</a>'
            ).format(pd[0].year, pd[0].url, pd[0].office_uk, pd[0].position_uk)
        return res

    pep_position_readable.short_description = _("Посада/остання декларація")
    pep_position_readable.allow_tags = True
    pep_position_readable.admin_order_field = "pep_position"

    def mark_for_application(self, request, queryset):
        queryset.update(status="a")

    mark_for_application.short_description = _("Статус: Застосувати зміну")

    def ignore(self, request, queryset):
        queryset.update(status="i")

    ignore.short_description = _("Статус: Ігнорувати зміну")

    def doublecheck(self, request, queryset):
        queryset.update(status="r")

    doublecheck.short_description = _("Статус: Потребує додаткової перевірки")

    actions = [mark_for_application, ignore, doublecheck]

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return (
            super(TerminationNoticeAdmin, self)
            .get_queryset(request)
            .prefetch_related("person")
        )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(TerminationNoticeAdmin, self).save_model(request, obj, form, change)


class AdHocMatchAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "pep_name_readable",
        "pep_position_readable",
        "dataset_entry_readable",
        "dataset_id",
        "name_match_score",
        "status",
    )

    list_editable = ("status",)
    list_filter = ("status", "dataset_id")

    search_fields = ("pep_name", "pep_position", "matched_json")

    def pep_name_readable(self, obj):
        if obj.person:
            return (
                (
                    '<a href="%s" target="_blank">%s %s %s</a><br/> %s<br/>%s'
                    % (
                        reverse("person_details", kwargs={"person_id": obj.person_id}),
                        obj.person.last_name_uk,
                        obj.person.first_name_uk,
                        obj.person.patronymic_uk,
                        (obj.person.also_known_as_uk or "").replace("\n", " ,"),
                        obj.person.date_of_birth,
                    )
                )
                .replace("  ", " ")
                .strip()
            )
        else:
            return obj.pep_name

    pep_name_readable.short_description = _("Прізвище з БД ПЕП")
    pep_name_readable.allow_tags = True
    pep_name_readable.admin_order_field = "pep_name"

    def dataset_entry_readable(self, obj):
        if obj.matched_json:
            return render_to_string("admin/dataset_entry.jinja", {"obj": obj})
        else:
            return ""

    dataset_entry_readable.short_description = _("Запис з датасету")
    dataset_entry_readable.allow_tags = True

    def pep_position_readable(self, obj):
        if obj.person:
            last_workplace = obj.person.last_workplace
            # TODO: Check I18n
            if last_workplace and last_workplace["position"] != "Клієнт банку":
                return '%s @ %s,<br/><span style="color: silver">%s</span>' % (
                    last_workplace["position"],
                    last_workplace["company"],
                    obj.person.get_type_of_official_display(),
                )
        else:
            return obj.pep_position

    pep_position_readable.short_description = _("Посада з БД PEP")
    pep_position_readable.allow_tags = True

    def mark_for_application(self, request, queryset):
        queryset.update(status="a")

    mark_for_application.short_description = _("Статус: Застосовано")

    def ignore(self, request, queryset):
        queryset.update(status="i")

    ignore.short_description = _("Статус: Ігнорувати")

    def doublecheck(self, request, queryset):
        queryset.update(status="r")

    doublecheck.short_description = _("Статус: Потребує додаткової перевірки")

    actions = [mark_for_application, ignore, doublecheck]

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(AdHocMatchAdmin, self).save_model(request, obj, form, change)


class WikiMatchAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/company_matcher.css",)}
        js = ("js/wiki_matcher.js",)

    list_display = (
        "pk",
        "pep_name_readable",
        "pep_position_readable",
        "wikidata_id",
        "dataset_entry_readable",
        "status",
    )

    list_editable = ("wikidata_id", "status")
    list_filter = ("status",)

    search_fields = ("pep_name", "pep_position", "matched_json")

    def pep_name_readable(self, obj):
        if obj.person:
            return (
                (
                    '<a href="%s" target="_blank">%s %s %s</a><br/> %s<br/>%s'
                    % (
                        reverse("person_details", kwargs={"person_id": obj.person_id}),
                        obj.person.last_name_uk,
                        obj.person.first_name_uk,
                        obj.person.patronymic_uk,
                        (obj.person.also_known_as_uk or "").replace("\n", " ,"),
                        obj.person.date_of_birth,
                    )
                )
                .replace("  ", " ")
                .strip()
            )
        else:
            return obj.pep_name

    pep_name_readable.short_description = _("Прізвище з БД ПЕП")
    pep_name_readable.allow_tags = True
    pep_name_readable.admin_order_field = "pep_name"

    def dataset_entry_readable(self, obj):
        if obj.matched_json:
            return render_to_string("admin/wiki_entry.jinja", {"obj": obj})
        else:
            return ""

    dataset_entry_readable.short_description = _("Записи з датасету")
    dataset_entry_readable.allow_tags = True

    def pep_position_readable(self, obj):
        if obj.person:
            last_workplace = obj.person.last_workplace
            # TODO: check I18n
            if last_workplace and last_workplace["position"] != "Клієнт банку":
                return '%s @ %s,<br/><span style="color: silver">%s</span>' % (
                    last_workplace["position"],
                    last_workplace["company"],
                    obj.person.get_type_of_official_display(),
                )
        else:
            return obj.pep_position

    pep_position_readable.short_description = _("Посада з БД PEP")
    pep_position_readable.allow_tags = True

    def mark_for_application(self, request, queryset):
        queryset.update(status="a")

    mark_for_application.short_description = _("Статус: Застосовано")

    def ignore(self, request, queryset):
        queryset.update(status="i")

    ignore.short_description = _("Статус: Ігнорувати")

    def doublecheck(self, request, queryset):
        queryset.update(status="r")

    doublecheck.short_description = _("Статус: Потребує додаткової перевірки")

    actions = [mark_for_application, ignore, doublecheck]

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(WikiMatchAdmin, self).save_model(request, obj, form, change)


class SMIDACandidateAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "company_readable",
        "smida_level",
        "smida_shares",
        "smida_name",
        "smida_parsed_name",
        "smida_is_real_person",
        "smida_position",
        "smida_position_class",
        "smida_position_body",
        "smida_yob",
        "smida_dt",
        "status",
    )

    list_editable = (
        "status",
        "smida_is_real_person",
        "smida_parsed_name",
        "smida_position_body",
        "smida_position_class",
    )
    list_filter = ("status",)

    search_fields = (
        "smida_name",
        "smida_position",
        "smida_edrpou",
        "smida_company_name",
        "smida_parsed_name",
    )

    def company_readable(self, obj):
        edrpou = unicode(obj.smida_edrpou).rjust(8, "0")

        return (
            '<a href="https://ring.org.ua/edr/uk/company/{}" target="_blank">{} ({})</a>'
        ).format(edrpou, obj.smida_company_name, edrpou)

    company_readable.short_description = _("Компанія")
    company_readable.allow_tags = True
    company_readable.admin_order_field = "smida_company_name"

    def mark_for_application(self, request, queryset):
        queryset.update(status="a")

    mark_for_application.short_description = _("Статус: Застосовано")

    def ignore(self, request, queryset):
        queryset.update(status="i")

    ignore.short_description = _("Статус: Ігнорувати")

    def doublecheck(self, request, queryset):
        queryset.update(status="r")

    doublecheck.short_description = _("Статус: Потребує додаткової перевірки")

    actions = [mark_for_application, ignore, doublecheck]

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(SMIDACandidateAdmin, self).save_model(request, obj, form, change)


admin.site.register(PersonDeduplication, PersonDeduplicationAdmin)
admin.site.register(CompanyDeduplication, CompanyDeduplicationAdmin)
admin.site.register(TerminationNotice, TerminationNoticeAdmin)
admin.site.register(AdHocMatch, AdHocMatchAdmin)
admin.site.register(WikiMatch, WikiMatchAdmin)

if settings.LANGUAGE_CODE == "uk":
    admin.site.register(CompanyMatching, CompanyMatchingAdmin)
    admin.site.register(BeneficiariesMatching, BeneficiariesMatchingAdmin)
    admin.site.register(EDRMonitoring, EDRMonitoringAdmin)
    admin.site.register(SMIDACandidate, SMIDACandidateAdmin)
