# coding: utf-8
from __future__ import unicode_literals
from django_markdown.utils import markdown as _markdown
from django_jinja import library
from django.utils.safestring import mark_safe


@library.filter
def markdown(*args, **kwargs):
    return _markdown(*args, **kwargs)


@library.global_function
def updated_querystring(request, params):
    """Updates current querystring with a given dict of params, removing
    existing occurrences of such params. Returns a urlencoded querystring."""
    original_params = request.GET.copy()
    for key in params:
        if key in original_params:
            original_params.pop(key)
    original_params.update(params)
    return original_params.urlencode()


@library.filter
def curformat(value):
    if value and value != "0":
        currency = ""
        if "$" in value:
            value = value.replace("$", "")
            currency = "USD "

        if "£" in value:
            value = value.replace("£", "")
            currency = "GBP "

        if "€" in value or "Є" in value:
            value = value.replace("€", "").replace("Є", "")
            currency = "EUR "

        try:
            return '{}{:,.2f}'.format(
                currency,
                float(value.replace(',', '.'))).replace(
                    ',', ' ').replace('.', ',')
        except ValueError:
            return value
    else:
        return mark_safe('<i class="i-value-empty">—</i>')
