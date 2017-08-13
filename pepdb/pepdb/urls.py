from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin
import django.contrib.sitemaps.views

from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailsearch import urls as wagtailsearch_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

from core.sitemaps import (
    MainXML, PersonXML, StaticXML, CompanyXML, CountriesXML)

import core.views


sitemaps = {
    'main': MainXML,
    'persons': PersonXML,
    'static': StaticXML,
    'companies': CompanyXML,
    'countries': CountriesXML
}


urlpatterns = i18n_patterns(
    # '',

    # Search
    url(r'^search$', core.views.search, name='search'),

    url(r'^search_person$', core.views.search, name='search_person',
        kwargs={"sources": ("persons",)}),
    url(r'^search_related$', core.views.search, name='search_related',
        kwargs={"sources": ("related",)}),
    url(r'^search_company$', core.views.search, name='search_company',
        kwargs={"sources": ("companies",)}),

    # Autocomplete
    url(r'^ajax/suggest$', core.views.suggest, name='suggest'),

    # Countries pages
    url(r'^countries/$', core.views.countries, name='countries'),
    url(r'^countries/(?P<country_id>[a-zA-Z]+)$', core.views.countries,
        name='countries'),

    # Persons/Companies
    url(r'^person/(?P<person_id>\d+)$', core.views.person_details,
        name='person_details'),

    url(r'^company/(?P<company_id>\d+)$', core.views.company_details,
        name='company_details'),

    # WS to feed graph ui
    url(r'connections/(?P<model>[a-zA-Z]+)/(?P<obj_id>[0-9]+)',
        core.views.connections, name="connections"),

    # Aux pages
    url(r'^feedback', TemplateView.as_view(template_name="feedback.jinja"),
        name="feedback"),


    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'', include(wagtail_urls)),
)

urlpatterns += [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^_send_feedback', core.views.send_feedback, name="send_feedback"),
    url(r'^sitemap.xml$', django.contrib.sitemaps.views.index,
        {'sitemaps': sitemaps}),

    url(r'^sitemap-(?P<section>.+).xml$',
        django.contrib.sitemaps.views.sitemap,
        {
            'sitemaps': sitemaps,
            'template_name': 'qartez/rel_alternate_hreflang_sitemap.xml'
        }),

    url(r'^grappelli/', include('grappelli.urls')),  # grappelli urls
    url(r'^redactor/', include('redactor.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^wg_search/', include(wagtailsearch_urls)),

    # PEP dataset
    url(r'^opendata/persons/(?P<fmt>(json|xml))',
        core.views.export_persons,
        name='export_persons'),

    # Short encrypted urls
    url(r'^p/(?P<enc>.*)',
        core.views.encrypted_redirect,
        name='encrypted_person_redirect',
        kwargs={"model": "Person"}),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
