from django.http import JsonResponse, Http404
from django.shortcuts import render
from operator import itemgetter
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
        persons = persons.query("match", _all=query)
        companies = companies.query("match", _all=query)
    else:
        persons = persons.query('match_all')
        companies = companies.query('match_all')

    return render(request, "search.jinja", {
        "persons": persons.filter("term", is_pep=True)[:6].execute(),
        "companies": companies[:6].execute(),
        "related_persons": persons.filter("term", is_pep=False)[:6].execute()
    })
