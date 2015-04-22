from operator import itemgetter

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from core.models import Person, Company
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


def search(request):
    query = request.GET.get("q", "")
    persons = ElasticPerson.search()
    companies = ElasticCompany.search()
    if query:
        persons = persons.query(
            "multi_match", query=query,
            fields=["full_name^2", "related_persons.person", "_all"])
        companies = companies.query(
            "multi_match", query=query,
            fields=["name^2", "short_name^2", "related_companies.company",
                    "_all"])
    else:
        persons = persons.query('match_all')
        companies = companies.query('match_all')

    return render(request, "search.jinja", {
        "persons": persons.filter("term", is_pep=True)[:6].execute(),
        "companies": companies[:6].execute(),
        "related_persons": persons.filter("term", is_pep=False)[:6].execute()
    })


def person_details(request, person_id):
    person = get_object_or_404(Person, pk=person_id)

    return render(request, "person.jinja", {
        "person": person
    })


def company_details(request, company_id):
    pass
