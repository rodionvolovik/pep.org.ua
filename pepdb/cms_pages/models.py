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

from core.utils import TranslatedField
from core.models import Person


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

    def localized_url(self, locale):
        translation.activate(locale)
        url = self.url
        translation.deactivate()
        return url


class StaticPage(AbstractJinjaPage, Page):
    body = RichTextField(verbose_name="Текст сторінки")
    template = "cms_pages/static_page.jinja"

    title_en = models.CharField(
        default="", max_length=255)

    body_en = RichTextField(
        default="",
        verbose_name="[EN] Текст сторінки")

    translated_title = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "title",
            "en": 'title_en'
        }
    )

    translated_body = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "body",
            "en": 'body_en'
        }
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
        **{
            settings.LANGUAGE_CODE: "caption",
            "en": 'caption_en'
        }
    )

    link_external = models.URLField("Зовнішнє посилання", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Або посилання на існуючу сторінку"
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Зображення"
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('caption_en'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page')
    ]

    class Meta:
        abstract = True


class HomePageTopMenuLink(Orderable, LinkFields):
    page = ParentalKey('cms_pages.HomePage', related_name='top_menu_links')


class HomePageBottomMenuLink(Orderable, LinkFields):
    page = ParentalKey('cms_pages.HomePage', related_name='bottom_menu_links')


class HomePage(AbstractJinjaPage, Page):
    template = "cms_pages/home.jinja"

    title_en = models.CharField(
        default="", max_length=255)

    subtitle = RichTextField(
        default="",
        verbose_name="[UA] Текст над пошуком")

    subtitle_en = RichTextField(
        default="",
        verbose_name="[EN] Текст над пошуком")

    body = RichTextField(
        default="",
        verbose_name="[UA] Текст під пошуком")

    body_en = RichTextField(
        default="",
        verbose_name="[EN] Текст під пошуком")

    credits = RichTextField(
        default="",
        verbose_name="[UA] Текст під статистикою")

    credits_en = RichTextField(
        default="",
        verbose_name="[EN] Текст під статистикою")

    eu_desc = RichTextField(
        default="",
        verbose_name="[UA] Текст про EU")

    eu_desc_en = RichTextField(
        default="",
        verbose_name="[EN] Текст про EU")

    tr_desc = RichTextField(
        default="",
        verbose_name="[UA] Текст про Thomson Reuters")

    tr_desc_en = RichTextField(
        default="",
        verbose_name="[EN] Текст про Thomson Reuters")

    footer = RichTextField(
        default="",
        verbose_name="[UA] Текст внизу кожної сторінки")

    footer_en = RichTextField(
        default="",
        verbose_name="[EN] Текст внизу кожної сторінки")

    translated_title = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "title",
            "en": 'title_en'
        }
    )

    translated_subtitle = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "subtitle",
            "en": 'subtitle_en'
        }
    )

    translated_body = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "body",
            "en": 'body_en'
        }
    )

    translated_credits = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "credits",
            "en": 'credits_en'
        }
    )

    translated_tr_desc = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "tr_desc",
            "en": 'tr_desc_en'
        }
    )

    translated_eu_desc = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "eu_desc",
            "en": 'eu_desc_en'
        }
    )

    translated_footer = TranslatedField(
        **{
            settings.LANGUAGE_CODE: "footer",
            "en": 'footer_en'
        }
    )

    class Meta:
        verbose_name = "Головна сторінка"

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('title_en', classname="full title"),

        FieldPanel('subtitle', classname="full title"),
        FieldPanel('subtitle_en', classname="full title"),

        FieldPanel('body', classname="full"),
        FieldPanel('body_en', classname="full"),

        FieldPanel('credits', classname="full"),
        FieldPanel('credits_en', classname="full"),

        FieldPanel('eu_desc', classname="full"),
        FieldPanel('eu_desc_en', classname="full"),
        FieldPanel('tr_desc', classname="full"),
        FieldPanel('tr_desc_en', classname="full"),

        InlinePanel('top_menu_links', label="Меню зверху"),
        InlinePanel('bottom_menu_links', label="Меню знизу"),

        FieldPanel('footer', classname="full"),
        FieldPanel('footer_en', classname="full"),
    ]

    def get_context(self, request, *args, **kwargs):
        ctx = super(HomePage, self).get_context(request, *args, **kwargs)

        ctx["persons_total"] = Person.objects.count()
        ctx["persons_pep"] = Person.objects.filter(type_of_official=1).count()
        ctx["persons_related"] = Person.objects.exclude(
            type_of_official=1).count()
        return ctx
