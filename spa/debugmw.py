"""TEMPORARY diagnostic middleware — reveals a traceback only when the request
carries ?t=<TOKEN>. Used to debug the Vercel 500; remove after fixing."""
import traceback

from django.http import HttpResponse

TOKEN = "trace-oasis-7x9q"


class DebugTracebackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if request.GET.get("t") == TOKEN:
            return HttpResponse(traceback.format_exc(),
                                content_type="text/plain", status=500)
        return None
