import sys
import six
from functools import wraps
from xml.sax.saxutils import XMLGenerator

from django.http import JsonResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render

from elasticsearch_dsl.response import Response
from elasticsearch_dsl.utils import AttrDict, AttrList, ObjectBase
from wagtail.wagtailsearch.backends.base import BaseSearchResults


def serialize_for_api(data):
    """Transform complex types that we use into simple ones recursively.
    Note: recursion isn't followed when we know that transformed types aren't
    supposed to contain any more complex types.

    TODO: this is rather ugly, would look better if views/models defined
    transformations explicitly. This is hard to achieve with function-based
    views, so it's pending a CBV move."""

    if hasattr(data, 'to_api'):
        return serialize_for_api(data.to_api())
    elif isinstance(data, Response):
        return serialize_for_api(data.hits._l_)
    elif isinstance(data, (AttrDict, ObjectBase)):
        return data.to_dict()
    elif isinstance(data, AttrList):
        return data._l_
    elif isinstance(data, dict):
        return {k: serialize_for_api(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return list(map(serialize_for_api, data))
    elif isinstance(data, BaseSearchResults):
        return None

    return data


def hybrid_response(template_name):
    """Returns either an HTML or JSON representation of the data that
    decorated function generates. Decision on format is based on "format" param
    in the query string, default is "html". For JSON serialization the data
    is passed through a recursive transformation into simple types.

    TODO: This would look better as a mixin for CBVs."""
    def hybrid_decorator(func):
        @wraps(func)
        def func_wrapper(request, *args, **kwargs):
            context = func(request, *args, **kwargs)
            if isinstance(context, HttpResponseBase):
                return context

            if request.GET.get('format', 'html') == 'json':
                return JsonResponse(serialize_for_api(context), safe=False)
            else:
                return render(request, template_name, context)
        return func_wrapper
    return hybrid_decorator


def is_listlike(x):
    """
    >>> is_listlike("foo")
    False
    >>> is_listlike(5)
    False
    >>> is_listlike(b"foo")
    False
    >>> is_listlike([b"foo"])
    True
    >>> is_listlike((b"foo",))
    True
    >>> is_listlike({})
    True
    >>> is_listlike(set())
    True
    >>> is_listlike((x for x in range(3)))
    True
    >>> is_listlike(six.moves.xrange(5))
    True
    """
    return hasattr(x, "__iter__") and not isinstance(x, (six.text_type, bytes))


# Serializer to XML, kindly borrowed from Scrapy Project:
# https://github.com/scrapy/scrapy/blob/master/scrapy/exporters.py
# Copyright (c) Scrapy developers.
class XmlItemExporter(object):
    def __init__(self, file, **kwargs):
        self.item_element = kwargs.pop('item_element', 'item')
        self.root_element = kwargs.pop('root_element', 'items')
        self.encoding = 'utf-8'
        self.xg = XMLGenerator(file, encoding=self.encoding)

    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement(self.root_element, {})

    def export_item(self, item):
        self.xg.startElement(self.item_element, {})
        for name, value in item.items():
            self._export_xml_field(name, value)
        self.xg.endElement(self.item_element)

    def finish_exporting(self):
        self.xg.endElement(self.root_element)
        self.xg.endDocument()

    def _export_xml_field(self, name, serialized_value):
        if (not serialized_value and
                not isinstance(serialized_value, (int, float, bool))):
            return

        self.xg.startElement(name, {})
        if hasattr(serialized_value, 'items'):
            for subname, value in serialized_value.items():
                self._export_xml_field(subname, value)
        elif is_listlike(serialized_value):
            for value in serialized_value:
                self._export_xml_field('value', value)
        elif isinstance(serialized_value, six.text_type):
            self._xg_characters(serialized_value)
        else:
            if isinstance(serialized_value, bool):
                serialized_value = int(serialized_value)
            self._xg_characters(str(serialized_value))
        self.xg.endElement(name)

    # Workaround for http://bugs.python.org/issue17606
    # Before Python 2.7.4 xml.sax.saxutils required bytes;
    # since 2.7.4 it requires unicode. The bug is likely to be
    # fixed in 2.7.6, but 2.7.6 will still support unicode,
    # and Python 3.x will require unicode, so ">= 2.7.4" should be fine.
    if sys.version_info[:3] >= (2, 7, 4):
        def _xg_characters(self, serialized_value):
            if not isinstance(serialized_value, six.text_type):
                serialized_value = serialized_value.decode(self.encoding)
            return self.xg.characters(serialized_value)
    else:  # pragma: no cover
        def _xg_characters(self, serialized_value):
            return self.xg.characters(serialized_value)
