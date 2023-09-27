import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django import http




class MyCorsMiddleware(MiddlewareMixin):
    CORS_DEFAULT_ALLOW_HEADERS = (
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    )
    CORS_ALLOW_METHODS = [
        'DELETE',
        'GET',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT',
    ]
    ACCESS_CONTROL_ALLOW_HEADERS = "Access-Control-Allow-Headers"
    ACCESS_CONTROL_ALLOW_METHODS = "Access-Control-Allow-Methods"
    ACCESS_CONTROL_ALLOW_ORIGIN = "Access-Control-Allow-Origin"

    def process_request(self, request):
        regex = 'api/'
        request.token = ''
        token = request.META.get('HTTP_API_KEY')
        if (
            request.path.find(regex) >= 0 and
            request.method == "OPTIONS"
            and "HTTP_ACCESS_CONTROL_REQUEST_METHOD" in request.META
        ):
            response = http.HttpResponse()
            response["Content-Length"] = "0"
            return response
    def process_response(self, req, resp):
        if settings.CORS_URLS_REGEX:
            expresion = re.compile(settings.CORS_URLS_REGEX, re.IGNORECASE)
            path = req.META.get('PATH_INFO')
            if expresion.match(path) != None:
                resp[self.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"

        if settings.CORS_ALLOW_HEADERS:
            resp[self.ACCESS_CONTROL_ALLOW_HEADERS] = self.get_headers()
        if req.method == "OPTIONS":
            resp[self.ACCESS_CONTROL_ALLOW_METHODS] = ", ".join(self.CORS_ALLOW_METHODS)
        return resp

    def get_headers(self):
        headers = ''
        heades_tuple = self.CORS_DEFAULT_ALLOW_HEADERS + settings.CORS_ALLOW_HEADERS
        for elem in heades_tuple:
            headers = headers + elem + ','
        return headers.strip(",")