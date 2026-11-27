from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class WwwRedirectMiddleware:
    """301-redirect www.<canonical host> to the canonical (apex) host."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.www_host = f'www.{settings.CANONICAL_HOST}'

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        if host == self.www_host:
            return HttpResponsePermanentRedirect(
                f'https://{settings.CANONICAL_HOST}{request.get_full_path()}'
            )
        return self.get_response(request)
