from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from projects.views import PROJECTS_DATA, tech_to_slug

# No lastmod is emitted: page content comes from a Python data structure and
# live GitHub READMEs, so neither the deploy date nor a repo's push date
# reliably reflects when a page's content actually changed.


class HttpsSitemap(Sitemap):
    protocol = 'https'


class StaticPagesSitemap(HttpsSitemap):
    priority = 0.8

    def items(self):
        return ['home', 'project_list', 'support', 'contact']

    def location(self, name):
        return reverse(name)


class ProjectSitemap(HttpsSitemap):
    priority = 0.7

    def items(self):
        return list(PROJECTS_DATA)

    def location(self, project_slug):
        return reverse('project_detail', args=[project_slug])


class RepositorySitemap(HttpsSitemap):
    priority = 0.6

    def items(self):
        return [
            (project['slug'], repo['slug'])
            for project in PROJECTS_DATA.values()
            for repo in project.get('repositories', [])
        ]

    def location(self, item):
        project_slug, repo_slug = item
        return reverse('repository_detail', args=[project_slug, repo_slug])


class TechSitemap(HttpsSitemap):
    priority = 0.4

    def items(self):
        techs = {
            tech_to_slug(tech)
            for project in PROJECTS_DATA.values()
            for repo in project.get('repositories', [])
            for tech in repo.get('tech_stack', [])
        }
        return sorted(techs)

    def location(self, tech_slug):
        return reverse('project_list_by_tech', args=[tech_slug])


sitemaps = {
    'static': StaticPagesSitemap,
    'projects': ProjectSitemap,
    'repositories': RepositorySitemap,
    'tech': TechSitemap,
}
