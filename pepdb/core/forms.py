# coding: utf-8
from __future__ import unicode_literals
from django.forms import ModelForm, Textarea, TextInput, Form, BooleanField, FileField
from core.models import FeedbackMessage
from django.utils.translation import ugettext_lazy as _
from captcha.fields import ReCaptchaField


class FeedbackForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = FeedbackMessage
        fields = ['person', 'text', 'link', 'email', 'contacts']

        widgets = {
            'person': TextInput(attrs={"class": "form-control input-md",
                                       "placeholder": _("ПІБ")}),
            'text': Textarea(attrs={"class": "form-control",
                                    "required": "",
                                    "rows": "3",
                                    "placeholder": _("Текст повідомлення")}),

            'link': TextInput(attrs={"class": "form-control input-md",
                                     "placeholder": _("http://")}),

            'email': TextInput(
                attrs={"class": "form-control input-md",
                       "required": "",
                       "placeholder": _("Ваш імейл")}),

            'contacts': TextInput(
                attrs={"class": "form-control input-md",
                       "placeholder": _("Ваш телефон")}),
        }


class EDRImportForm(Form):
    csv = FileField(required=True)
    is_state_companies = BooleanField(
        required=False,
        help_text=u"Керівники усіх компанії з файлу є ПЕПами"
    )


class ForeignImportForm(Form):
    csv = FileField(required=True)
