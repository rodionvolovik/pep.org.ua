import re
from django.utils.translation.trans_real import (
    parse_accept_lang_header, language_code_re)


class LocaleHackMiddleware(object):
    """
    This is a very ugly middleware
    """

    def process_request(self, request):
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')

        for accept_lang, _ in parse_accept_lang_header(accept):
            if accept_lang == 'uk':
                request.META['HTTP_ACCEPT_LANGUAGE'] = accept.replace(
                    'uk', 'ua', 1)
