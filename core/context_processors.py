from django.conf import settings


def canonical_url(request):
    """Expose the canonical URL for the current page, plus the site root.

    Always the https apex host plus the path, with no query string, so that
    www and tracking-parameter variants all point search engines at one URL.
    `site_url` is used to make absolute URLs (e.g. og:image), which social
    networks require.
    """
    site_url = f'https://{settings.CANONICAL_HOST}'
    return {
        'canonical_url': f'{site_url}{request.path}',
        'site_url': site_url,
    }
