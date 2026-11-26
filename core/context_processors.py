from django.conf import settings


def canonical_url(request):
    """Expose the canonical URL for the current page.

    Always the https apex host plus the path, with no query string, so that
    www and tracking-parameter variants all point search engines at one URL.
    """
    return {'canonical_url': f'https://{settings.CANONICAL_HOST}{request.path}'}
