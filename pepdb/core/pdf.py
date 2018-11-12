from functools import wraps

from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import HttpResponseBase

import weasyprint


def pdf_response(template_name):
    """Returns either an HTML or PDF representation of the data that
    decorated function generates. Decision on format is based on "format" param
    in the query string, default is "html". For PDF print CSS is used"""

    def pdf_decorator(func):
        @wraps(func)
        def func_wrapper(request, *args, **kwargs):
            context = func(request, *args, **kwargs)
            if isinstance(context, HttpResponseBase):
                return context

            if request.GET.get("format", "html") == "pdf":
                context["disable_css"] = True

                html = render(request, template_name, context).content

                base_url = request.build_absolute_uri("/")
                pdf = weasyprint.HTML(string=html, base_url=base_url).write_pdf()

                response = HttpResponse(content=pdf, content_type="application/pdf")

                if "filename" in context:
                    response["Content-Disposition"] = (
                        "attachment; filename=%s.pdf" % context["filename"]
                    )
                else:
                    response["Content-Disposition"] = "attachment"

                return response
            else:
                return render(request, template_name, context)

        return func_wrapper

    return pdf_decorator
