# coding: utf-8
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField


class StaticPage(Page):
    body = RichTextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    def get_context(self, request, *args, **kwargs):
        return {
            'self': self,
            'page': self,
            'request': request,
        }

    class Meta:
        verbose_name = "Статична сторінка"


StaticPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]
