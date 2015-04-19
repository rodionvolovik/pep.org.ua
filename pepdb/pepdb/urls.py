from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='home.jinja'),
        name="home"),

    url(r'^ajax/suggest$', 'core.views.suggest', name='suggest'),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli urls
    url(r'^markdown/', include('django_markdown.urls')),  # django_markdown url
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
