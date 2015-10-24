from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

from django.contrib import admin

from core.sitemaps import MainXML, PersonXML, StaticXML

sitemaps = {
    'main': MainXML,
    'persons': PersonXML,
    'static': StaticXML,
}

from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailsearch import urls as wagtailsearch_urls


urlpatterns = i18n_patterns(
    # '',

    url(r'^search$', 'core.views.search', name='search'),
    url(r'^search_person$', 'core.views.search', name='search_person',
        kwargs={"sources": ["persons"]}),
    url(r'^search_related$', 'core.views.search', name='search_related',
        kwargs={"sources": ["related"]}),

    url(r'^person/(?P<person_id>\d+)$', 'core.views.person_details',
        name='person_details'),

    # url(r'^company/(?P<company_id>\d+)$$', 'core.views.company_details',
    #     name='company_details'),

    url(r'^sitemap-(?P<section>.+).xml$',
        'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps}),

    url(r'', include(wagtail_urls)),
)

urlpatterns += [
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.index',
        {'sitemaps': sitemaps}),

    url(r'^ajax/suggest$', 'core.views.suggest', name='suggest'),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli urls
    url(r'^markdown/', include('django_markdown.urls')),  # django_markdown url
    url(r'^admin/', include(admin.site.urls)),

    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^wg_search/', include(wagtailsearch_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
