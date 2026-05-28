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
