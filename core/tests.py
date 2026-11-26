from django.test import TestCase, RequestFactory
from django.core.cache import cache
from .forms import ContactForm
from .views import check_rate_limit


class ContactFormHoneypotTests(TestCase):
    def _valid_data(self, **kwargs):
        data = {'name': 'Alice', 'email': 'alice@example.com', 'message': 'Hello', 'website': ''}
        data.update(kwargs)
        return data

    def test_empty_honeypot_passes(self):
        form = ContactForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_filled_honeypot_fails(self):
        form = ContactForm(data=self._valid_data(website='http://spam.example.com'))
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_missing_required_fields_fails(self):
        form = ContactForm(data={'website': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)

    def test_invalid_email_fails(self):
        form = ContactForm(data=self._valid_data(email='not-an-email'))
        self.assertFalse(form.is_valid())


class CheckRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def tearDown(self):
        cache.clear()

    def _make_request(self, ip='1.2.3.4'):
        request = self.factory.post('/contact/')
        request.META['REMOTE_ADDR'] = ip
        return request

    def test_first_three_submissions_allowed(self):
        for _ in range(3):
            self.assertTrue(check_rate_limit(self._make_request()))

    def test_fourth_submission_blocked(self):
        for _ in range(3):
            check_rate_limit(self._make_request())
        self.assertFalse(check_rate_limit(self._make_request()))

    def test_different_ips_are_independent(self):
        for _ in range(3):
            check_rate_limit(self._make_request(ip='1.1.1.1'))
        # Different IP should still be allowed
        self.assertTrue(check_rate_limit(self._make_request(ip='2.2.2.2')))

    def test_same_ip_blocked_after_limit(self):
        ip = '5.5.5.5'
        for _ in range(3):
            check_rate_limit(self._make_request(ip=ip))
        self.assertFalse(check_rate_limit(self._make_request(ip=ip)))


class SitemapTests(TestCase):
    def test_sitemap_lists_all_pages(self):
        from projects.views import PROJECTS_DATA
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('https://testserver/</loc>', content)
        self.assertIn('https://testserver/projects/</loc>', content)
        self.assertNotIn('<lastmod>', content)
        for slug, project in PROJECTS_DATA.items():
            self.assertIn(f'/projects/{slug}/</loc>', content)
            for repo in project['repositories']:
                self.assertIn(f'/projects/{slug}/{repo["slug"]}/</loc>', content)

    def test_robots_txt_points_to_sitemap(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sitemap: https://testserver/sitemap.xml', response.content.decode())


class CanonicalUrlTests(TestCase):
    def test_home_has_canonical_without_query_string(self):
        response = self.client.get('/?utm_source=x')
        self.assertContains(response, '<link rel="canonical" href="https://turnpiece.com/">', html=False)

    def test_inner_page_canonical_uses_path(self):
        response = self.client.get('/projects/')
        self.assertContains(response, '<link rel="canonical" href="https://turnpiece.com/projects/">', html=False)


class WwwRedirectTests(TestCase):
    def test_www_redirects_permanently_to_apex(self):
        with self.settings(ALLOWED_HOSTS=['www.turnpiece.com']):
            response = self.client.get('/projects/?a=1', HTTP_HOST='www.turnpiece.com')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://turnpiece.com/projects/?a=1')

    def test_apex_is_not_redirected(self):
        with self.settings(ALLOWED_HOSTS=['turnpiece.com']):
            response = self.client.get('/', HTTP_HOST='turnpiece.com')
        self.assertEqual(response.status_code, 200)
