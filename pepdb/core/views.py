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
    return render(request, "search.jinja", {

    })
