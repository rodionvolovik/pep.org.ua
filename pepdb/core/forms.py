# coding: utf-8
from __future__ import unicode_literals
from django.forms import ModelForm, Textarea, TextInput
from core.models import FeedbackMessage
from django.utils.translation import ugettext_lazy as _
from captcha.fields import ReCaptchaField


class FeedbackForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = FeedbackMessage
        fields = ['person', 'text', 'link']

        widgets = {
            'person': TextInput(attrs={"class": "form-control input-md",
                                       "placeholder": _("ПІБ")}),
            'text': Textarea(attrs={"class": "form-control",
                                    "required": "",
                                    "rows": "5",
                                    "placeholder": _("Текст повідомлення")}),

            'link': TextInput(attrs={"class": "form-control input-md",
                                     "placeholder": _("http://")}),
        }
