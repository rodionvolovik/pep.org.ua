from operator import itemgetter

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from core.models import Person
from core.paginator import paginated_search
from core.elastic_models import (
    Person as ElasticPerson,
    Company as ElasticCompany)


def suggest(request):
    results = []

    search = ElasticPerson.search()\
        .suggest(
            'name',
            request.GET.get('q', ''),
            completion={
                'field': 'full_name_suggest',
                'size': 7,
                'fuzzy': {
                    'fuzziness': 3,
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
            request.GET.get('q', ''),
            completion={
                'field': 'name_suggest',
                'size': 3,
                'fuzzy': {
                    'fuzziness': 3,
                    'unicode_aware': 1
                }
            }
    )

    res = search.execute()
    if res.success:
        results += res.suggest['name'][0]['options']

    results = sorted(results, key=itemgetter("score"), reverse=True)

    if results:
        return JsonResponse(
            [val['text'] for val in results],
            safe=False
        )
    else:
        return JsonResponse([], safe=False)


def search(request, sources=["persons", "related"]):
    params = {}

    if "persons" in sources:
        params["persons"] = _search_person(request)

    if "related" in sources:
        params["related_persons"] = _search_related(request)

    return render(request, "search.jinja", params)


def _search_person(request):
    query = request.GET.get("q", "")
    is_exact = request.GET.get("is_exact", "") == "on"

    persons = ElasticPerson.search()

    if query:
        persons = persons.query(
            "multi_match", query=query,
            fields=["full_name^2", "related_persons.person", "_all"])

        persons = persons.filter("term", is_pep=True)
    else:
        persons = persons.query('match_all')
        persons = persons.filter("term", is_pep=True)

    return paginated_search(request, persons)


def _search_related(request):
    query = request.GET.get("q", "")
    is_exact = request.GET.get("is_exact", "") == "on"

    related_persons = ElasticPerson.search()

    if query:
        related_persons = related_persons.query(
            "multi_match", query=query,
            fields=["full_name^2", "related_persons.person", "_all"])
    else:
        related_persons = related_persons.query('match_all')
        related_persons = related_persons.filter("term", is_pep=False)

    return paginated_search(request, related_persons)


def person_details(request, person_id):
    person = get_object_or_404(Person, pk=person_id)

    return render(request, "person.jinja", {
        "person": person
    })


def company_details(request, company_id):
    pass
