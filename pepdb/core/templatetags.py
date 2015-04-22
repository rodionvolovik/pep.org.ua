from django_markdown.utils import markdown as _markdown
from django_jinja import library


@library.filter
def markdown(*args, **kwargs):
    return _markdown(*args, **kwargs)
