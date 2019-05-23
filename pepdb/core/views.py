from __future__ import unicode_literals
from operator import itemgetter
from datetime import datetime
from cStringIO import StringIO
from django.http import (
    JsonResponse,
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    Http404,
)
from django.utils import translation
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.apps import apps
from django.db.models import Count, F
from django.conf import settings
from django.views.decorators.cache import never_cache

from elasticsearch_dsl.query import Q
from translitua import translit
from cryptography.fernet import InvalidToken

from core.models import Person, Declaration, Country, Company, ActionLog
from core.pdf import pdf_response
from core.utils import (
    is_cyr,
    add_encrypted_url,
    unique,
    blacklist,
    localized_field,
    localized_fields,
    get_localized_field,
)
from core.paginator import paginated_search
from core.forms import FeedbackForm
from core.auth import logged_in_or_basicauth
from core.api import XmlItemExporter


from core.elastic_models import Person as ElasticPerson, Company as ElasticCompany


def suggest(request):
    lang = translation.get_language()
    field = localized_field("full_name", lang)
    company_field = localized_field("name_suggest_output", lang)

    def assume(q, fuzziness):
        results = []

        search = (
            ElasticPerson.search()
            .source(["full_name_suggest", field])
            .params(size=0)
            .suggest(
                "name",
                q,
                completion={
                    "field": "full_name_suggest",
                    "size": 10,
                    "fuzzy": {"fuzziness": fuzziness, "unicode_aware": True},
                },
            )
        )

        res = search.execute()
        if res.success:
            results += res.suggest["name"][0]["options"]

        search = (
            ElasticCompany.search()
            .source(["name_suggest", company_field])
            .params(size=0)
            .suggest(
                "name",
                q,
                completion={
                    "field": "name_suggest",
                    "size": 5,
                    "fuzzy": {"fuzziness": fuzziness, "unicode_aware": True},
                },
            )
        )

        # TODO: Investigate, completion doesn't work with numbers

        res = search.execute()
        if res.success:
            results += res.suggest["name"][0]["options"]

        results = sorted(results, key=itemgetter("_score"), reverse=True)

        if results:
            return unique(
                getattr(val._source, company_field, "")
                or getattr(val._source, field, "")
                for val in results
            )
        else:
            return []

    q = request.GET.get("q", "").strip()

    # It seems, that for some reason 'AUTO' setting doesn't work properly
    # for unicode strings
    fuzziness = 0

    if len(q) > 3:
        fuzziness = 1

    suggestions = assume(q, fuzziness)

    if not suggestions:
        suggestions = assume(q, fuzziness + 1)

    return JsonResponse(suggestions, safe=False)


def search(request, sources=("persons", "companies")):
    query = request.GET.get("q", "")
    is_exact = request.GET.get("is_exact", "") == "on"

    params = {"query": query, "sources": sources, "today": datetime.now()}

    if is_exact:
        persons = ElasticPerson.search().query(
            "multi_match",
            query=query,
            operator="and",
            fields=["names"]
            + localized_fields(
                ["full_name", "also_known_as"], langs=settings.LANGUAGE_CODES
            ),
        )

        # Special case when we were looking for one exact person and found it.
        if persons.count() == 1:
            person = persons.execute()[0]

            return redirect(reverse("person_details", kwargs={"person_id": person.id}))

        companies = ElasticCompany.search().query(
            "multi_match",
            query=query,
            operator="and",
            fields=localized_fields(
                ["short_name", "name"], langs=settings.LANGUAGE_CODES
            ),
        )

        # Special case when we were looking for one exact company and found it.
        if companies.count() == 1:
            company = companies.execute()[0]

            return redirect(
                reverse("company_details", kwargs={"company_id": company.id})
            )

    try:
        if "persons" in sources:
            params["persons"] = _search_person(request)

            if not params["persons"]:
                params["suggested_person"] = _suggest_person(request)

        if "companies" in sources:
            params["companies"] = _search_company(request)
    except EmptyPage:
        raise Http404("Page is empty")
    except PageNotAnInteger:
        raise Http404("No page")

    return render(request, "search.jinja", params)


def _search_person(request):
    query = request.GET.get("q", "")
    _fields = ["names^2"]

    for lang in settings.LANGUAGE_CODES:
        _fields.append(localized_field("full_name", lang) + "^3")
        _fields.append(localized_field("also_known_as", lang) + "^2")
        _fields.append(localized_field("related_persons.person", lang))

    if query:
        persons = ElasticPerson.search().query(
            Q(
                "bool",
                should=[Q("match", is_pep=True)],
                must=[Q("multi_match", query=query, operator="and", fields=_fields)],
            )
        )
    else:
        persons = ElasticPerson.search().query("match_all")

    for lang in settings.LANGUAGE_CODES:
        persons = persons.highlight(
            localized_field("related_persons.person", lang),
            order="score",
            pre_tags=[""],
            post_tags=[""],
        )

    return paginated_search(request, persons, settings.CATALOG_PER_PAGE * 2)


def _suggest_person(request):
    query = request.GET.get("q", "")
    if query:
        _fields = ["names^2"]

        for lang in settings.LANGUAGE_CODES:
            _fields.append(localized_field("full_name", lang) + "^3")
            _fields.append(localized_field("also_known_as", lang) + "^2")
            _fields.append(localized_field("related_persons.person", lang))

        persons = ElasticPerson.search().query(
            Q(
                "bool",
                should=[Q("match", is_pep=True)],
                must=[
                    Q(
                        "multi_match",
                        query=query,
                        operator="and",
                        fields=_fields,
                        fuzziness="auto",
                    )
                ],
            )
        )[:1]

        res = persons.execute()

        if res:
            return res[0]


def _search_company(request):
    query = request.GET.get("q", "")
    _fields = [
        "other_founders",
        "other_recipient",
        "other_owners",
        "other_managers",
        "bank_name",
        "edrpou",
        "code_chunks",
    ] + localized_fields(
        ["name", "short_name", "related_persons.person"], langs=settings.LANGUAGE_CODES
    )

    if query:
        companies = ElasticCompany.search().query(
            "multi_match", query=query, operator="and", fields=_fields
        )

        if companies.count() == 0:
            # PLAN B, PLAN B
            companies = ElasticCompany.search().query(
                "multi_match",
                query=query,
                operator="or",
                minimum_should_match="2",
                fields=_fields,
            )

    else:
        companies = ElasticCompany.search().query("match_all")

    for lang in settings.LANGUAGE_CODES:
        companies = companies.highlight(
            localized_field("related_persons.person", lang),
            order="score",
            pre_tags=[""],
            post_tags=[""],
        )

    return paginated_search(
        request,
        # We are using highlight here to find which exact related person
        # caused the match to show it in the person's card on the top of the
        # list. Check Person.relevant_related_persons method for details
        companies,
    )


@pdf_response("person.jinja")
def person_details(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    context = {
        "person": person,
        "query": "",
        "all_declarations": person.get_declarations(),
    }

    full_name = "%s %s %s" % (person.last_name, person.first_name, person.patronymic)

    if is_cyr(full_name):
        context["filename"] = translit(
            full_name.lower().strip().replace(" ", "_").replace("\n", "")
        )
    else:
        context["filename"] = person.pk

    context["feedback_form_override"] = FeedbackForm(
        initial={"person": unicode(person)}
    )

    return context


def countries(request, sources=("persons", "companies"), country_id=None):
    country = None
    if country_id is not None:
        country = get_object_or_404(Country, iso2=country_id)

    used_countries = (
        Country.objects.annotate(
            persons_count=Count("person2country", distinct=True),
            companies_count=Count("company2country", distinct=True),
        )
        .annotate(usages=F("persons_count") + F("companies_count"))
        .exclude(usages=0)
        .exclude(iso2="")
        .order_by("-usages")
    )

    params = {"used_countries": used_countries, "country": country}

    if "persons" in sources:
        if country_id is None:
            persons = ElasticPerson.search().query("match_all")
        else:
            persons = ElasticPerson.search().query(
                "match",
                **{
                    localized_field("related_countries__to_country"): {
                        "query": get_localized_field(country, "name"),
                        "operator": "and",
                    }
                }
            )

    if "companies" in sources:
        if country_id is None:
            companies = ElasticCompany.search().query("match_all")
        else:
            companies = ElasticCompany.search().query(
                "match",
                **{
                    localized_field("related_countries__to_country"): {
                        "query": get_localized_field(country, "name"),
                        "operator": "and",
                    }
                }
            )

    try:
        params["persons"] = paginated_search(request, persons)
        params["companies"] = paginated_search(request, companies)
    except EmptyPage:
        raise Http404("Page is empty")
    except PageNotAnInteger:
        raise Http404("No page")

    return render(request, "countries.jinja", params)


@pdf_response("company.jinja")
def company_details(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    context = {"company": company}

    if is_cyr(company.name):
        context["filename"] = translit(
            company.name.lower().strip().replace(" ", "_").replace("\n", "")
        )
    else:
        context["filename"] = company.pk

    context["feedback_form_override"] = FeedbackForm(
        initial={"person": unicode(company.name)}
    )

    return context


def send_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            form.save()

            return render(request, "_thank_you.jinja")
    else:
        form = FeedbackForm()

    return render(request, "_feedback_form.jinja", {"feedback_form_override": form})


@logged_in_or_basicauth()
@never_cache
def export_persons(request, fmt):
    if not request.user.has_perm("core.export_persons"):
        return HttpResponseForbidden()

    if request.user.has_perm("core.export_id_and_last_modified"):
        fields_to_blacklist = []
    else:
        fields_to_blacklist = ["id", "last_change"]

    data = map(
        lambda p: blacklist(
            add_encrypted_url(p, request.user, "encrypted_person_redirect"),
            fields_to_blacklist,
        ),
        ElasticPerson.get_all_persons(),
    )

    ActionLog(user=request.user, action="download_dataset", details=fmt).save()

    if fmt == "json":
        response = JsonResponse(data, safe=False)

    if fmt == "xml":
        fp = StringIO()
        xim = XmlItemExporter(fp)
        xim.start_exporting()

        for item in data:
            xim.export_item(item)

        xim.finish_exporting()
        payload = fp.getvalue()
        fp.close()
        response = HttpResponse(payload, content_type="application/xhtml+xml")

    response[
        "Content-Disposition"
    ] = "attachment; filename=peps_{:%Y%m%d_%H%M}.{}".format(datetime.now(), fmt)

    response["Content-Length"] = len(response.content)

    return response


@logged_in_or_basicauth()
@never_cache
def export_companies(request, fmt):
    if not request.user.has_perm("core.export_companies"):
        return HttpResponseForbidden()

    data = map(
        lambda p: blacklist(
            add_encrypted_url(p, request.user, "encrypted_company_redirect"), ["id"]
        ),
        ElasticCompany.get_all_companies(),
    )

    ActionLog(
        user=request.user, action="download_companies_dataset", details=fmt
    ).save()

    if fmt == "json":
        response = JsonResponse(data, safe=False)

    if fmt == "xml":
        fp = StringIO()
        xim = XmlItemExporter(fp)
        xim.start_exporting()

        for item in data:
            xim.export_item(item)

        xim.finish_exporting()
        payload = fp.getvalue()
        fp.close()
        response = HttpResponse(payload, content_type="application/xhtml+xml")

    response[
        "Content-Disposition"
    ] = "attachment; filename=companies_{:%Y%m%d_%H%M}.{}".format(datetime.now(), fmt)

    response["Content-Length"] = len(response.content)

    return response


def encrypted_redirect(request, enc, model):
    try:
        decrypted = settings.SYMMETRIC_ENCRYPTOR.decrypt(bytes(enc))
        user_id, obj_id = map(int, decrypted.split("|"))
    except (InvalidToken, ValueError):
        return HttpResponseBadRequest()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponseForbidden()

    model = apps.get_model("core", model)
    try:
        obj = model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return HttpResponseNotFound()

    return redirect(obj.get_absolute_url())


def connections(request, model, obj_id):
    if model.lower() not in ("person", "country", "company"):
        return HttpResponseBadRequest()

    model = apps.get_model("core", model)

    try:
        obj = model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return HttpResponseNotFound()

    node_info = obj.get_node_info(True)

    node_info["nodes"][0]["data"]["is_main"] = True

    return JsonResponse(node_info)
