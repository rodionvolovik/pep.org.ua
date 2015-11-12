from core.forms import FeedbackForm


def feedback_processor(request):
    return {
        'feedback_form': FeedbackForm()
    }
