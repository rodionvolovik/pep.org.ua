from __future__ import unicode_literals
from operator import itemgetter

from django.http import JsonResponse
from django.utils import translation
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse

from elasticsearch_dsl.query import Q
from translitua import translit

from core.models import Person, Declaration
from core.api import hybrid_response
from core.pdf import pdf_response
from core.utils import is_cyr
from core.paginator import paginated_search
from core.forms import FeedbackForm

from core.elastic_models import (
    Person as ElasticPerson,
    Company as ElasticCompany)


def suggest(request):
    if translation.get_language() == "en":
        field = 'full_name_suggest_en'
    else:
        field = 'full_name_suggest'

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
                    'field': 'name_suggest',
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


@hybrid_response("search.jinja")
def search(request, sources=["persons", "related"]):
    params = {}

    query = request.GET.get("q", "")
    is_exact = request.GET.get("is_exact", "") == "on"

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

    if "persons" in sources:
        params["persons"] = _search_person(request)

    if "related" in sources:
        params["related_persons"] = _search_related(request)

    return params


def _search_person(request):
    query = request.GET.get("q", "")

    if query:
        persons = ElasticPerson.search().query(
            "multi_match", query=query,
            operator="and",
            fields=["full_name", "names"])

        persons = persons.filter("term", is_pep=True)

        if persons.count() == 0:
            # PLAN B, PLAN B
            persons = ElasticPerson.search().query(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=["full_name", "names"])

            persons = persons.filter("term", is_pep=True)
    else:
        persons = ElasticPerson.search().query('match_all')
        persons = persons.filter("term", is_pep=True)

    return paginated_search(request, persons)


def _search_related(request):
    query = request.GET.get("q", "")

    if query:
        all_related = Q(
            "multi_match", query=query,
            operator="and",
            fields=["related_persons.person_uk", "related_persons.person_en"])

        non_peps = Q(
            "multi_match", query=query,
            operator="and",
            fields=["full_name", "names"]) & Q("match", is_pep=False)

        related_persons = ElasticPerson.search().query(all_related | non_peps)

        if related_persons.count() == 0:
            # PLAN B, PLAN B
            all_related = Q(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=["related_persons.person_uk",
                        "related_persons.person_en"])

            non_peps = Q(
                "multi_match", query=query,
                operator="or",
                minimum_should_match="2",
                fields=["full_name", "names"]) & Q("match", is_pep=False)

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


def company_details(request, company_id):
    pass


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
