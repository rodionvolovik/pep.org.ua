from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from core.models import Person
from cms_pages.models import StaticPage


class MainXML(sitemaps.Sitemap):
    changefreq = 'daily'

    def items(self):
        pages = [
            ('wagtail_serve', ['']),
        ]
        return pages

    def location(self, item):
        return reverse(item[0], args=item[1])


class PersonXML(sitemaps.Sitemap):
    def items(self):
        return Person.objects.all()

    def location(self, item):
        return item.get_absolute_url()


class StaticXML(sitemaps.Sitemap):
    def items(self):
        return list(StaticPage.objects.live())

    def location(self, item):
        return item.url
