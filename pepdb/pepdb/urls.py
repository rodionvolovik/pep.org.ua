from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin

from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailsearch import urls as wagtailsearch_urls


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='home.jinja'),
        name="home"),

    url(r'^search$', 'core.views.search', name='search'),
    url(r'^search_person$', 'core.views.search', name='search_person',
        kwargs={"sources": ["persons"]}),
    url(r'^search_related$', 'core.views.search', name='search_related',
        kwargs={"sources": ["related"]}),

    url(r'^person/(?P<person_id>\d+)$', 'core.views.person_details',
        name='person_details'),

    # url(r'^company/(?P<company_id>\d+)$$', 'core.views.company_details',
    #     name='company_details'),

    url(r'^ajax/suggest$', 'core.views.suggest', name='suggest'),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli urls
    url(r'^markdown/', include('django_markdown.urls')),  # django_markdown url
    url(r'^admin/', include(admin.site.urls)),

    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^wg_search/', include(wagtailsearch_urls)),

    url(r'', include(wagtail_urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
