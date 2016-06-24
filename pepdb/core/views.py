from __future__ import unicode_literals
from operator import itemgetter

from django.http import JsonResponse
from django.utils import translation
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.db.models import Count, F

from elasticsearch_dsl.query import Q
from translitua import translit

from core.models import Person, Declaration, Country, Company
from core.pdf import pdf_response
from core.utils import is_cyr
from core.paginator import paginated_search
from core.forms import FeedbackForm

from core.elastic_models import (
    Person as ElasticPerson,
    Company as ElasticCompany)


def suggest(request):
    if translation.get_language() == "en":
        field = "full_name_suggest_en"
        company_field = "name_suggest_en"
    else:
        field = "full_name_suggest"
        company_field = "name_suggest"

    def assume(q, fuzziness):
        results = []

        search = ElasticPerson.search()\
            .suggest(
                'name',
                q,
                completion={
                    'field': field,
                    'size': 10,
                    'fuzzy': {
                        'fuzziness': fuzziness,
                        'unicode_aware': 1
                    }
                }
        )

        res = search.execute()
        if res.success:
            results += res.suggest['name'][0]['options']

        search = ElasticCompany.search()\
            .suggest(
                'name',
                q,
                completion={
                    'field': company_field,
                    'size': 5,
                    'fuzzy': {
                        'fuzziness': fuzziness,
                        'unicode_aware': 1
                    }
                }
        )

        res = search.execute()
        if res.success:
            results += res.suggest['name'][0]['options']

        results = sorted(results, key=itemgetter("score"), reverse=True)

        if results:
            return [val['text'] for val in results]
        else:
            []

    q = request.GET.get('q', '').strip()

    # It seems, that for some reason 'AUTO' setting doesn't work properly
    # for unicode strings
    fuzziness = 0

    if len(q) > 3:
        fuzziness = 1

    suggestions = assume(q, fuzziness)

    if not suggestions:
        suggestions = assume(q, fuzziness + 1)

    return JsonResponse(suggestions, safe=False)


def search(request, sources=("persons", "related", "companies")):
    query = request.GET.get("q", "")
    is_exact = request.GET.get("is_exact", "") == "on"

    params = {
        "query": query,
        "sources": sources
    }

    if is_exact:
        persons = ElasticPerson.search().query(
            "multi_match", query=query,
            operator="and",
            fields=["full_name", "names"])

        # Special case when we were looking for one exact person and found it.
        if persons.count() == 1:
            person = persons.execute()[0]

            return redirect(
                reverse("person_details",
                        kwargs={"person_id": person.id})
            )

        companies = ElasticCompany.search().query(
            "multi_match", query=query,
            operator="and",
            fields=["short_name_en", "short_name_uk", "name_en", "name_uk"])

        # Special case when we were looking for one exact person and found it.
        if companies.count() == 1:
            company = companies.execute()[0]

            return redirect(
                reverse("company_details",
                        kwargs={"company_id": company.id})
            )

    if "persons" in sources:
        params["persons"] = _search_person(request)

    if "related" in sources:
        params["related_persons"] = _search_related(request)

    if "companies" in sources:
        params["companies"] = _search_company(request)

    return render(request, "search.jinja", params)


def _search_person(request):
    query = request.GET.get("q", "")
    _fields = ["full_name", "names"]

    if query:
        persons = ElasticPerson.search().query(
            "multi_match", query=query,
            operator="and",
            fields=_fields)

        persons = persons.filter("term", is_pep=True)

        if persons.count() == 0:
            # PLAN B, PLAN B
            persons = ElasticPerson.search().query(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=_fields)

            persons = persons.filter("term", is_pep=True)
    else:
        persons = ElasticPerson.search().query('match_all')
        persons = persons.filter("term", is_pep=True)

    return paginated_search(request, persons)


def _search_company(request):
    query = request.GET.get("q", "")
    _fields = ["name_uk", "short_name_uk", "name_en", "short_name_en",
               "related_persons.person_uk", "related_persons.person_en",
               "other_founders", "other_recipient", "other_owners",
               "other_managers", "bank_name"]

    if query:
        companies = ElasticCompany.search().query(
            "multi_match", query=query,
            operator="and",
            fields=_fields)

        if companies.count() == 0:
            # PLAN B, PLAN B
            companies = ElasticCompany.search().query(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=_fields)

            companies = companies.filter("term", is_pep=True)
    else:
        companies = ElasticCompany.search().query('match_all')

    return paginated_search(
        request,
        # We are using highlight here to find which exact related person
        # caused the match to show it in the person's card on the top of the
        # list. Check Person.relevant_related_persons method for details
        companies.highlight(
            'related_persons.person_uk',
            order="score", pre_tags=[""], post_tags=[""]).highlight(
            'related_persons.person_en',
            order="score", pre_tags=[""], post_tags=[""])
    )


def _search_related(request):
    query = request.GET.get("q", "")
    _fields = ["related_persons.person_uk", "related_persons.person_en"]
    _fields_pep = ["full_name", "names"]

    if query:
        all_related = Q(
            "multi_match", query=query,
            operator="and",
            fields=_fields)

        non_peps = Q(
            "multi_match", query=query,
            operator="and",
            fields=_fields_pep) & Q("match", is_pep=False)

        related_persons = ElasticPerson.search().query(all_related | non_peps)

        if related_persons.count() == 0:
            # PLAN B, PLAN B
            all_related = Q(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=_fields)

            non_peps = Q(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=_fields_pep) & Q("match", is_pep=False)

            related_persons = ElasticPerson.search().query(
                all_related | non_peps)

    else:
        related_persons = ElasticPerson.search().query(
            'match_all').filter("term", is_pep=False)

    return paginated_search(
        request,
        # We are using highlight here to find which exact related person
        # caused the match to show it in the person's card on the top of the
        # list. Check Person.relevant_related_persons method for details
        related_persons.highlight(
            'related_persons.person_uk',
            order="score", pre_tags=[""], post_tags=[""]).highlight(
            'related_persons.person_en',
            order="score", pre_tags=[""], post_tags=[""])
    )


@pdf_response("person.jinja")
def person_details(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    context = {
        "person": person,
        "declarations": Declaration.objects.filter(
            person=person, confirmed="a").order_by("year")
    }

    full_name = "%s %s %s" % (
        person.last_name_uk, person.first_name_uk, person.patronymic_uk)

    if is_cyr(full_name):
        context["filename"] = translit(full_name.lower().replace(" ", "_"))
    else:
        context["filename"] = person.pk

    context["feedback_form_override"] = FeedbackForm(initial={
        "person": unicode(person)
    })

    return context


def countries(request, sources=("persons", "companies"), country_id=None):
    country = None
    if country_id is not None:
        country = get_object_or_404(Country, iso2=country_id)

    used_countries = Country.objects.annotate(
        persons_count=Count("person2country"),
        companies_count=Count("company2country")).annotate(
        usages=F("persons_count") + F("companies_count")).exclude(
        usages=0, iso2="").order_by("-usages")

    params = {
        "used_countries": used_countries,
        "country": country
    }

    if "persons" in sources:
        if country_id is None:
            persons = ElasticPerson.search().query('match_all')
        else:
            persons = ElasticPerson.search().query(
                'match', related_countries__to_country_uk=country.name_uk)

    if "companies" in sources:
        if country_id is None:
            companies = ElasticCompany.search().query('match_all')
        else:
            companies = ElasticCompany.search().query(
                'match', related_countries__to_country_uk=country.name_uk)

    params["persons"] = paginated_search(request, persons)
    params["companies"] = paginated_search(request, companies)

    return render(request, "countries.jinja", params)


@pdf_response("company.jinja")
def company_details(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    context = {
        "company": company,
    }

    if is_cyr(company.name_uk):
        context["filename"] = translit(
            company.name_uk.lower().replace(" ", "_"))
    else:
        context["filename"] = company.pk

    context["feedback_form_override"] = FeedbackForm(initial={
        "person": unicode(company.name)
    })

    return context


def send_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            form.save()

            return render(request, "_thank_you.jinja")
    else:
        form = FeedbackForm()

    return render(request, "_feedback_form.jinja", {
        "feedback_form_override": form
    })
