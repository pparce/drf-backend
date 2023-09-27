from django.utils.deprecation import MiddlewareMixin


class TokenRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        regex = 'api/v1.0/'