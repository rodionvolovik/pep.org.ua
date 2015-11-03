from django.core.urlresolvers import reverse

from core.models import Person
from cms_pages.models import StaticPage
from qartez import RelAlternateHreflangSitemap
from django.conf import settings


class MainXML(RelAlternateHreflangSitemap):
    changefreq = 'daily'

    def items(self):
        pages = [
            ('wagtail_serve', ['']),
        ]
        return pages

    def location(self, item):
        return reverse(item[0], args=item[1])

    def alternate_hreflangs(self, obj):
        return [
            (lang, "%s/%s/" % (settings.SITE_URL, lang))
            for lang, _ in settings.LANGUAGES]


class PersonXML(RelAlternateHreflangSitemap):
    def items(self):
        return Person.objects.all()

    def location(self, item):
        return item.get_absolute_url()

    def alternate_hreflangs(self, obj):
        return [
            (lang, "%s%s" % (settings.SITE_URL, obj.localized_url(lang)))
            for lang, _ in settings.LANGUAGES]


class StaticXML(RelAlternateHreflangSitemap):
    def items(self):
        return list(StaticPage.objects.live())

    def location(self, item):
        return item.url

    def alternate_hreflangs(self, obj):
        return [
            (lang, "%s%s" % (settings.SITE_URL, obj.localized_url(lang)))
            for lang, _ in settings.LANGUAGES]
