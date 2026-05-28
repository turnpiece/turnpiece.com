from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.core.cache import cache

from .views import convert_markdown_to_html, PROJECTS_DATA


class ConvertMarkdownToHtmlTests(TestCase):
    def test_h1_header(self):
        result = convert_markdown_to_html('# Hello World')
        self.assertIn('<h1>', result)
        self.assertIn('Hello World', result)

    def test_h2_header(self):
        result = convert_markdown_to_html('## Sub-heading')
        self.assertIn('<h2>', result)
        self.assertIn('Sub-heading', result)

    def test_bold(self):
        result = convert_markdown_to_html('**bold text**')
        self.assertIn('<strong>', result)
        self.assertIn('bold text', result)

    def test_inline_code(self):
        result = convert_markdown_to_html('`inline code`')
        self.assertIn('<code>', result)
        self.assertIn('inline code', result)

    def test_fenced_code_block(self):
        result = convert_markdown_to_html('```\nblock of code\n```')
        self.assertIn('<code>', result)
        self.assertIn('block of code', result)

    def test_unordered_list(self):
        result = convert_markdown_to_html('- item one\n- item two')
        self.assertIn('<ul>', result)
        self.assertIn('<li>', result)
        self.assertIn('item one', result)

    def test_link(self):
        result = convert_markdown_to_html('[click here](https://example.com)')
        self.assertIn('<a ', result)
        self.assertIn('href="https://example.com"', result)
        self.assertIn('click here', result)

    def test_image(self):
        result = convert_markdown_to_html('![alt text](https://example.com/img.png)')
        self.assertIn('<img ', result)
        self.assertIn('https://example.com/img.png', result)
        self.assertIn('alt text', result)

    def test_returns_string(self):
        self.assertIsInstance(convert_markdown_to_html('hello'), str)

    def test_empty_input(self):
        result = convert_markdown_to_html('')
        self.assertIsInstance(result, str)


class ProjectListViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_filter_returns_all_projects(self):
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        self.assertEqual(len(projects), len(PROJECTS_DATA))

    def test_flutter_filter_returns_only_temphist(self):
        response = self.client.get('/projects/tech/flutter/')
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        slugs = [p['slug'] for p in projects]
        self.assertIn('temphist', slugs)
        self.assertNotIn('portfolio', slugs)

    def test_python_filter_includes_both_projects(self):
        # Both temphist (API repo) and portfolio use Python
        response = self.client.get('/projects/tech/python/')
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        slugs = [p['slug'] for p in projects]
        self.assertIn('temphist', slugs)
        self.assertIn('portfolio', slugs)

    def test_filter_sets_context_variables(self):
        response = self.client.get('/projects/tech/django/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tech_slug'], 'django')
        self.assertEqual(response.context['filtered_tech'], 'Django')

    def test_unknown_tech_slug_returns_empty(self):
        response = self.client.get('/projects/tech/cobol/')
        self.assertEqual(response.status_code, 200)
        projects = response.context['projects']
        self.assertEqual(len(projects), 0)


class RepositoryDetailViewTests(TestCase):
    FAKE_README = '# TempHist App\n\nThis is the **readme** content.'
    FAKE_COMMIT_DATE = '2026-05-18T12:00:00Z'  # 10 days before test date (2026-05-28)

    def setUp(self):
        cache.clear()
        self.client = Client()

    def tearDown(self):
        cache.clear()

    def _make_mock_response(self, url, *args, **kwargs):
        mock_resp = MagicMock()
        if 'raw.githubusercontent.com' in url:
            mock_resp.status_code = 200
            mock_resp.text = self.FAKE_README
        elif '/commits/main' in url:
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                'commit': {
                    'committer': {
                        'date': self.FAKE_COMMIT_DATE
                    }
                }
            }
        else:
            mock_resp.status_code = 404
        return mock_resp

    @patch('projects.views.requests.get')
    def test_readme_content_rendered(self, mock_get):
        mock_get.side_effect = self._make_mock_response
        response = self.client.get('/projects/temphist/app/')
        self.assertEqual(response.status_code, 200)
        content = response.context['content']
        self.assertIn('<h1>', content)
        self.assertIn('TempHist App', content)
        self.assertIn('<strong>', content)

    @patch('projects.views.requests.get')
    def test_last_updated_set_from_commit(self, mock_get):
        mock_get.side_effect = self._make_mock_response
        response = self.client.get('/projects/temphist/app/')
        self.assertEqual(response.status_code, 200)
        last_updated = response.context['last_updated']
        self.assertIsNotNone(last_updated)
        self.assertIn('days ago', last_updated)

    @patch('projects.views.requests.get')
    def test_readme_cached_on_second_request(self, mock_get):
        mock_get.side_effect = self._make_mock_response
        self.client.get('/projects/temphist/app/')
        self.client.get('/projects/temphist/app/')
        # README fetch should only happen once (commit fetch also once)
        readme_calls = [c for c in mock_get.call_args_list
                        if 'raw.githubusercontent.com' in c.args[0]]
        self.assertEqual(len(readme_calls), 1)

    @patch('projects.views.requests.get')
    def test_github_error_shows_fallback_message(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp
        response = self.client.get('/projects/temphist/app/')
        self.assertEqual(response.status_code, 200)
        content = response.context['content']
        self.assertIn('Unable to load', content)

    def test_invalid_project_returns_404(self):
        response = self.client.get('/projects/nonexistent/repo/')
        self.assertEqual(response.status_code, 404)

    def test_invalid_repo_slug_returns_404(self):
        response = self.client.get('/projects/temphist/nonexistent/')
        self.assertEqual(response.status_code, 404)
