# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from django.utils import translation

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore.whitelist import (
    attribute_rule, allow_without_attributes)
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel, FieldPanel, PageChooserPanel, MultiFieldPanel)


@hooks.register('construct_whitelister_element_rules')
def whitelister_element_rules():
    return {
        'u': allow_without_attributes,
        'table': attribute_rule({'cellspacing': True, 'cellpadding': True,
                                 'border': True}),
        'td': attribute_rule({'valign': True, 'style': True}),
        'tr': allow_without_attributes,
        'th': allow_without_attributes,
        'tbody': allow_without_attributes,
        'tfoot': allow_without_attributes,
        'thead': allow_without_attributes,
        'p': attribute_rule({'align': True}),
    }


class TranslatedField(object):
    def __init__(self, ua_field, en_field):
        self.ua_field = ua_field
        self.en_field = en_field

    def __get__(self, instance, owner):
        if translation.get_language() == 'en':
            return getattr(instance, self.en_field)
        else:
            return getattr(instance, self.ua_field)


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

    title_en = models.CharField(
        default="", max_length=255)

    body_en = RichTextField(
        default="",
        verbose_name="[EN] Текст сторінки")

    translated_title = TranslatedField(
        'title',
        'title_en',
    )

    translated_body = TranslatedField(
        'body',
        'body_en',
    )

    class Meta:
        verbose_name = "Статична сторінка"


StaticPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('title_en', classname="full title"),
    FieldPanel('body', classname="full"),
    FieldPanel('body_en', classname="full"),
]


class LinkFields(models.Model):
    caption = models.CharField(max_length=255, blank=True,
                               verbose_name="Заголовок")
    caption_en = models.CharField(max_length=255, blank=True,
                                  verbose_name="[EN] Заголовок")

    translated_caption = TranslatedField(
        'caption',
        'caption_en',
    )

    link_external = models.URLField("Зовнішнє посилання", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Або посилання на існуючу сторінку"
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('caption'),
        FieldPanel('caption_en'),
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
        related_name='+',
        verbose_name="Зображення"
    )

    panels = [
        ImageChooserPanel('image'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class ColumnFields(models.Model):
    title = models.CharField(
        max_length=255, blank=True, verbose_name="Заголовок")
    body = RichTextField(verbose_name="Текст колонки")

    title_en = models.CharField(
        verbose_name="[EN] Заголовок", default="", max_length=255)

    body_en = RichTextField(
        default="", verbose_name="[EN] Текст колонки")

    translated_title = TranslatedField(
        'title',
        'title_en',
    )

    translated_body = TranslatedField(
        'body',
        'body_en',
    )

    panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('title_en', classname="full title"),
        FieldPanel('body', classname="full"),
        FieldPanel('body_en', classname="full"),
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

    title_en = models.CharField(
        default="", max_length=255)

    body = RichTextField(
        default="",
        verbose_name="[UA] Текст на блакитній панелі")

    body_en = RichTextField(
        default="",
        verbose_name="[EN] Текст на блакитній панелі")

    translated_title = TranslatedField(
        'title',
        'title_en',
    )

    translated_body = TranslatedField(
        'body',
        'body_en',
    )

    class Meta:
        verbose_name = "Головна сторінка"

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('title_en', classname="full title"),
        FieldPanel('body', classname="full"),
        FieldPanel('body_en', classname="full"),

        InlinePanel('top_menu_links', label="Меню зверху"),
        InlinePanel('columns', label="Колонки під пошуком"),
        InlinePanel('banner_items', label="Банери спонсорів"),
        InlinePanel('bottom_menu_links', label="Меню знизу"),
    ]
