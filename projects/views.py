from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
import os
import requests
import mistune
from datetime import datetime, timezone


def github_headers():
    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

def tech_to_slug(tech_name):
    """Convert tech name to URL slug."""
    tech_mapping = {
        'Python': 'python',
        'Flutter': 'flutter',
        'Dart': 'dart',
        'JavaScript': 'javascript',
        'PHP': 'php',
        'HTML': 'html',
        'CSS': 'css',
        'FastAPI': 'fastapi',
        'PostgreSQL': 'postgresql',
        'Firebase': 'firebase',
        'WordPress': 'wordpress',
        'Django': 'django',
        'Redis': 'redis',
    }
    return tech_mapping.get(tech_name, tech_name.lower().replace(' ', '-'))

# Single source of truth for project data
PROJECTS_DATA = {
    'temphist': {
        'slug': 'temphist',
        'name': 'TempHist',
        'description': 'Historical temperature visualisation and analysis platform',
        'colour': '#242456',  # Dark blue colour
        'logo_svg': 'assets/temphist-logo.svg',
        'logo_png': 'assets/temphist-logo.png',
        'overview': 'TempHist is a platform for visualising and analysing historical temperature data, compare the today\'s temperature with the temperatures on the same date and in the same location over the past 50 years. The project consists of an API that provides temperature data and analysis, along with a mobile app and a website that visualise the data.',
        'repositories': [
            {
                'name': 'Mobile app',
                'slug': 'app',
                'description': 'iOS app for exploring historical temperature data',
                'github_url': 'https://github.com/turnpiece/temphist_app',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/temphist_app/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/temphist_app',
                'tech_stack': ['Flutter', 'Dart', 'Firebase'],
                'custom_description': 'The TempHist iOS app lets you see how today\'s temperature compares with historical records for the same date. Browse by day, week, month or year, search for any location in the world, and share snapshots with friends.',
                'features': [
                    'Horizontal bar chart showing temperatures across decades',
                    'Daily, weekly, monthly and yearly views',
                    'Location selection with search',
                    'Social sharing',
                    'Available on iOS',
                    'Firebase-powered real-time data',
                ],
                'screenshots': [
                    {'src': 'assets/TempHist-iPhone-screenshot.png', 'alt': 'TempHist iOS app', 'caption': 'Temperature history at a glance'},
                ],
            },
            {
                'name': 'Temphist.com',
                'slug': 'website',
                'url': 'https://temphist.com',
                'description': 'Web app for historical temperature visualisation',
                'github_url': 'https://github.com/turnpiece/TempHist',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/TempHist/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/TempHist',
                'tech_stack': ['HTML', 'CSS', 'JavaScript', 'Firebase'],
                'custom_description': 'The TempHist website brings historical temperature data to any browser. Use your own location or pick from a range of cities around the world and see how temperatures have shifted over the past 50 years — all presented as an easy-to-read chart. See how today compares with the same date in previous years, or how this past week compares with the week ending on the same date in previous years, or this past month or past year. Is it warmer or cooler than average for the time of year? Are temperatures rising or falling?',
                'features': [
                    'Temperature history visualisation for your location',
                    'Daily, weekly, monthly and yearly views',
                    'Location selection — browse any place in the world',
                    'Social sharing of temperature snapshots',
                    'Responsive design for mobile and desktop',
                ],
                'screenshot': 'assets/TempHist-website-screenshot.png',
            },
            {
                'name': 'API',
                'slug': 'api',
                'description': 'Backend API and data services',
                'github_url': 'https://github.com/turnpiece/TempHist-API',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/TempHist-API/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/TempHist-API',
                'tech_stack': ['Python', 'FastAPI', 'Redis', 'PostgreSQL'],
                'custom_description': 'The TempHist API powers the app and website. It fetches and aggregates historical temperature records for any location worldwide, with Redis caching to keep responses fast even for repeated queries.',
                'features': [
                    'Historical temperature data for any location worldwide',
                    'Daily, weekly, monthly and yearly aggregated endpoints',
                    'Redis caching for fast repeated queries',
                    'Authentication and rate limiting',
                    'OpenAPI/Swagger documentation',
                ],
                'logo': 'assets/temphist-logo.png'
            }
        ]
    },
    'portfolio': {
        'slug': 'portfolio',
        'name': 'Turnpiece',
        'description': 'The website you are looking at right now',
        'logo_svg': 'assets/tp-logo-white-transparent-fixed.svg',
        'logo_png': 'assets/tp-logo-white-transparent-fixed.png',
        'overview': 'This is a Python Django application that pulls live README documentation and repository metadata directly from GitHub, so the content stays up to date without manual editing.',
        'repositories': [
            {
                'name': 'Turnpiece.com',
                'slug': 'website',
                'url': 'https://turnpiece.com',
                'description': 'Django-powered portfolio website with live GitHub integration',
                'github_url': 'https://github.com/turnpiece/turnpiece.com',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/turnpiece.com/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/turnpiece.com',
                'tech_stack': ['Python', 'Django', 'PostgreSQL', 'HTML', 'CSS'],
                'screenshot': 'assets/turnpiece-com-homepage-screenshot.png',
                'custom_description': 'Built with Django and Tailwind CSS, this site pulls live README content and last-updated dates directly from GitHub via the public API. Projects, tech stacks and features are defined in a single Python data structure — no database needed for content.',
                'features': [
                    'Live README documentation pulled from GitHub on each visit',
                    'GitHub last-updated date shown on every repository page',
                    'Tech-stack filtering across all projects',
                    'Rate-limited contact form with honeypot spam protection',
                    'Deployed on Railway with PostgreSQL',
                ],
            }
        ]
    }
}

def project_list_view(request, tech_slug=None):
    """List all projects, optionally filtered by tech stack."""
    # Convert PROJECTS_DATA to list format for the list view
    projects = list(PROJECTS_DATA.values())
    for project in projects:
        for repo in project['repositories']:
            repo['project_slug'] = project['slug']
    
    # Filter by tech stack if specified
    if tech_slug:
        # Convert tech_slug back to proper case (e.g., 'python' -> 'Python')
        tech_mapping = {
            'python': 'Python',
            'flutter': 'Flutter',
            'dart': 'Dart',
            'javascript': 'JavaScript',
            'php': 'PHP',
            'html': 'HTML',
            'css': 'CSS',
            'fastapi': 'FastAPI',
            'postgresql': 'PostgreSQL',
            'firebase': 'Firebase',
            'wordpress': 'WordPress',
            'graphic-package': 'Graphic package',
            'django': 'Django',
            'redis': 'Redis',
        }
        tech_name = tech_mapping.get(tech_slug.lower(), tech_slug.title())
        
        # Filter projects to only show those with the specified tech
        filtered_projects = []
        for project in projects:
            project_uses_tech = any(
                tech_name in repo.get('tech_stack', [])
                for repo in project['repositories']
            )
            if project_uses_tech:
                for repo in project['repositories']:
                    repo['project_slug'] = project['slug']
                filtered_projects.append(project)
        
        projects = filtered_projects
        context = {
            "projects": projects,
            "filtered_tech": tech_name,
            "tech_slug": tech_slug
        }
    else:
        context = {"projects": projects}
    
    return render(request, "projects/project_list.html", context)

def project_detail_view(request, project_slug):
    """Show project overview with all repositories."""
    project = PROJECTS_DATA.get(project_slug)
    if not project:
        return render(request, "projects/404.html", status=404)
    
    # Add project slug to each repository for URL generation
    for repo in project['repositories']:
        repo['project_slug'] = project_slug
    
    return render(request, "projects/project_detail.html", {"project": project})

def repository_detail_view(request, project_slug, repo_slug):
    """Show individual repository documentation."""
    # Use the centralized PROJECTS_DATA as single source of truth
    projects = PROJECTS_DATA
    
    project = projects.get(project_slug)
    if not project:
        return render(request, "projects/404.html", status=404)
    
    # Find the repository in the repositories list
    repositories = project.get("repositories", [])
    repo_info = None
    for repo in repositories:
        if repo.get("slug") == repo_slug:
            repo_info = repo
            break
    
    if not repo_info:
        return render(request, "projects/404.html", status=404)
    
    # Add project context
    repo_info['project_name'] = project['name']
    repo_info['project_slug'] = project_slug
    repo_info['readme_page_url'] = repo_info['github_url'] + '/blob/main/README.md'

    # Fetch README content from GitHub — cached for 1 hour
    readme_cache_key = f"github_readme_{project_slug}_{repo_slug}"
    html_content = cache.get(readme_cache_key)
    if not html_content:
        try:
            response = requests.get(repo_info['readme_url'], timeout=10, headers=github_headers())
            if response.status_code == 200:
                html_content = convert_markdown_to_html(response.text)
            else:
                html_content = "<p>Unable to load documentation from GitHub.</p>"
        except Exception as e:
            html_content = f"<p>Error loading documentation: {str(e)}</p>"
        cache.set(readme_cache_key, html_content, 3600)

    # Fetch latest commit on main branch — cached for 1 hour
    last_updated = None
    if repo_info.get('api_url'):
        cache_key = f"github_main_commit_{project_slug}_{repo_slug}"
        commit_data = cache.get(cache_key)
        if not commit_data:
            try:
                commit_resp = requests.get(
                    f"{repo_info['api_url']}/commits/main", timeout=5,
                    headers=github_headers()
                )
                if commit_resp.status_code == 200:
                    commit_data = commit_resp.json()
                    cache.set(cache_key, commit_data, 3600)
            except Exception:
                pass
        if commit_data:
            committed_at = commit_data.get('commit', {}).get('committer', {}).get('date')
            if committed_at:
                dt = datetime.fromisoformat(committed_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                delta = now - dt
                if delta.days == 0:
                    last_updated = 'today'
                elif delta.days == 1:
                    last_updated = 'yesterday'
                elif delta.days < 30:
                    last_updated = f'{delta.days} days ago'
                elif delta.days < 365:
                    months = delta.days // 30
                    last_updated = f'{months} month{"s" if months > 1 else ""} ago'
                else:
                    last_updated = dt.strftime('%-d %B %Y')

    return render(request, "projects/repository_detail.html", {
        "content": html_content,
        "repo_info": repo_info,
        "last_updated": last_updated,
    })

def convert_markdown_to_html(markdown_text):
    return mistune.html(markdown_text)
