from core.forms import FeedbackForm
from django.conf import settings


def feedback_processor(request):
    return {
        'feedback_form': FeedbackForm(),
    }

def config_processor(request):
    return {
        'SITE_URL': settings.SITE_URL,
    }
