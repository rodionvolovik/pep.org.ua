from core.forms import FeedbackForm
from django.conf import settings
from core.models import Country


def feedback_processor(request):
    return {"feedback_form": FeedbackForm()}


def config_processor(request):
    return {
        "SITE_URL": settings.SITE_URL,
        "SITEHEART_ID": settings.SITEHEART_ID,
        "GA_ID": settings.GA_ID,
        "LANGUAGE_CODES": settings.LANGUAGE_CODES,
        "DEFAULT_LANGUAGE_CODE": settings.LANGUAGE_CODE,
    }
