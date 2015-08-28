# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.html import mark_safe

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore.whitelist import (
    attribute_rule, check_url, allow_without_attributes)
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel, FieldPanel, PageChooserPanel, MultiFieldPanel)


@hooks.register('construct_whitelister_element_rules')
def whitelister_element_rules():
    return {
        'u': allow_without_attributes,
        'p': attribute_rule({'align': True}),
    }


class AbstractJinjaPage(object):
    @hooks.register('insert_editor_js')
    def editor_js():
        return mark_safe(
            """
            <script>
                registerHalloPlugin(
                  "halloformat", {
                  "formattings": {
                     "bold": true,
                     "italic": true,
                     "strikethrough": false,
                     "underline": true
                }});

                registerHalloPlugin("hallojustify", {});
            </script>
            """
        )

    @hooks.register('insert_editor_css')
    def editor_css():
        return mark_safe(
            '<link rel="stylesheet" href="' + settings.STATIC_URL +
            'css/font-awesome.min.css">' +
            '<link rel="stylesheet" href="' + settings.STATIC_URL +
            'css/fucking-icons.css">')

    def get_context(self, request, *args, **kwargs):
        return {
            'self': self,
            'page': self,
            'request': request,
        }


class StaticPage(AbstractJinjaPage, Page):
    body = RichTextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    class Meta:
        verbose_name = "Статична сторінка"


StaticPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]


class LinkFields(models.Model):
    caption = models.CharField(max_length=255, blank=True)

    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('caption'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page')
    ]

    class Meta:
        abstract = True


class BannerItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        ImageChooserPanel('image'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class ColumnFields(models.Model):
    title = models.CharField(max_length=255, blank=True)
    body = RichTextField(verbose_name="Текст колонки")

    panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('body', classname="full"),
    ]


class HomePageBannerItem(Orderable, BannerItem):
    page = ParentalKey('cms_pages.HomePage', related_name='banner_items')


class HomePageTopMenuLink(Orderable, LinkFields):
    page = ParentalKey('cms_pages.HomePage', related_name='top_menu_links')


class HomePageBottomMenuLink(Orderable, LinkFields):
    page = ParentalKey('cms_pages.HomePage', related_name='bottom_menu_links')


class HomePageColumn(Orderable, ColumnFields):
    page = ParentalKey('cms_pages.HomePage', related_name='columns')


class HomePage(AbstractJinjaPage, Page):
    template = "cms_pages/home.jinja"

    body = RichTextField(
        default="",
        verbose_name="Текст на блакитній панелі")

    class Meta:
        verbose_name = "Головна сторінка"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    InlinePanel(HomePage, 'top_menu_links', label="Меню зверху"),
    InlinePanel(HomePage, 'banner_items', label="Банери спонсорів"),
    InlinePanel(HomePage, 'bottom_menu_links', label="Меню знизу"),
]
