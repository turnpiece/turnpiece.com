from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
import requests
import re
from datetime import datetime, timezone

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
        'Graphic Package': 'graphic-package',
        'Django': 'django',
        'Tailwind CSS': 'tailwind-css',
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
                'name': 'Mobile App',
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
                    {'src': '/static/assets/TempHist-iPhone-screenshot.png', 'alt': 'TempHist iOS app', 'caption': 'Temperature history at a glance'},
                ],
            },
            {
                'name': 'Website',
                'slug': 'website',
                'url': 'https://temphist.org',
                'description': 'Web app for historical temperature visualisation',
                'github_url': 'https://github.com/turnpiece/TempHist',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/TempHist/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/TempHist',
                'tech_stack': ['HTML', 'CSS', 'JavaScript', 'Firebase'],
                'custom_description': 'The TempHist website brings historical temperature data to any browser. Pick a location anywhere in the world, choose a time range, and see how temperatures have shifted over the past 50 years — all presented as an easy-to-read chart.',
                'features': [
                    'Temperature history visualisation for your location',
                    'Daily, weekly, monthly and yearly views',
                    'Location selection — browse any place in the world',
                    'Social sharing of temperature snapshots',
                    'Responsive design for mobile and desktop',
                ],
                'screenshot': '/static/assets/TempHist-website-screenshot.png',
            },
            {
                'name': 'API',
                'slug': 'api',
                'description': 'Backend API and data services',
                'github_url': 'https://github.com/turnpiece/TempHist-API',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/TempHist-API/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/TempHist-API',
                'tech_stack': ['Python', 'FastAPI', 'Redis'],
                'custom_description': 'The TempHist API powers the app and website. It fetches and aggregates historical temperature records for any location worldwide, with Redis caching to keep responses fast even for repeated queries.',
                'features': [
                    'Historical temperature data for any location worldwide',
                    'Daily, weekly, monthly and yearly aggregated endpoints',
                    'Redis caching for fast repeated queries',
                    'Authentication and rate limiting',
                    'OpenAPI/Swagger documentation',
                ],
                'logo': '/static/assets/temphist-logo.png',
            }
        ]
    },
    'portfolio': {
        'slug': 'portfolio',
        'name': 'This Portfolio',
        'description': 'The website you are looking at right now',
        'logo_svg': 'assets/tp-logo-white-transparent-fixed.svg',
        'logo_png': 'assets/tp-logo-white-transparent-fixed.png',
        'overview': 'This portfolio site is itself an active project. It is a Django application that pulls live README documentation and repository metadata directly from GitHub, so the content stays up to date without manual editing.',
        'repositories': [
            {
                'name': 'Portfolio Website',
                'slug': 'website',
                'url': 'https://turnpiece.com',
                'description': 'Django-powered portfolio with live GitHub integration',
                'github_url': 'https://github.com/turnpiece/turnpiece.com',
                'readme_url': 'https://raw.githubusercontent.com/turnpiece/turnpiece.com/main/README.md',
                'api_url': 'https://api.github.com/repos/turnpiece/turnpiece.com',
                'tech_stack': ['Python', 'Django', 'Tailwind CSS', 'PostgreSQL'],
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
            'graphic-package': 'Graphic Package',
            'django': 'Django',
            'tailwind-css': 'Tailwind CSS',
            'redis': 'Redis',
        }
        tech_name = tech_mapping.get(tech_slug.lower(), tech_slug.title())
        
        # Filter projects to only show those with the specified tech
        filtered_projects = []
        for project in projects:
            # Check if any repository in this project uses the tech
            project_uses_tech = False
            for repo in project['repositories']:
                if tech_name in repo.get('tech_stack', []):
                    project_uses_tech = True
                    break
            
            if project_uses_tech:
                # Include the complete project with all repositories
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

    try:
        # Fetch README content from GitHub
        response = requests.get(repo_info['readme_url'], timeout=10)
        if response.status_code == 200:
            readme_content = response.text
            html_content = convert_markdown_to_html(readme_content)
        else:
            html_content = "<p>Unable to load documentation from GitHub. Please check the repository URL.</p>"
    except Exception as e:
        html_content = f"<p>Error loading documentation: {str(e)}</p>"

    # Fetch GitHub repo metadata (last push date) — cached for 1 hour
    last_updated = None
    if repo_info.get('api_url'):
        cache_key = f"github_meta_{project_slug}_{repo_slug}"
        github_meta = cache.get(cache_key)
        if not github_meta:
            try:
                meta_resp = requests.get(
                    repo_info['api_url'], timeout=5,
                    headers={'Accept': 'application/vnd.github+json'}
                )
                if meta_resp.status_code == 200:
                    github_meta = meta_resp.json()
                    cache.set(cache_key, github_meta, 3600)
            except Exception:
                pass
        if github_meta:
            pushed_at = github_meta.get('pushed_at')
            if pushed_at:
                dt = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
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
    """Basic markdown to HTML conversion."""
    # Convert headers
    markdown_text = re.sub(r'^### (.*$)', r'<h3>\1</h3>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^## (.*$)', r'<h2>\1</h2>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^# (.*$)', r'<h2>\1</h2>', markdown_text, flags=re.MULTILINE)  # Convert H1 to H2
    
    # Convert bold and italic
    markdown_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown_text)
    markdown_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', markdown_text)
    
    # Convert code blocks
    markdown_text = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', markdown_text, flags=re.DOTALL)
    markdown_text = re.sub(r'`(.*?)`', r'<code>\1</code>', markdown_text)
    
    # Convert links
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', markdown_text)
    
    # Convert lists - first pass: convert list items to HTML
    lines = markdown_text.split('\n')
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* ') or stripped.startswith('- '):
            processed_lines.append(re.sub(r'^[\*\-] (.*$)', r'<li>\1</li>', line, flags=re.MULTILINE))
        elif re.match(r'^\d+\. ', stripped):
            processed_lines.append(re.sub(r'^\d+\. (.*$)', r'<li>\1</li>', line, flags=re.MULTILINE))
        else:
            processed_lines.append(line)
    
    # Second pass: wrap list items in ul/ol tags with proper start attributes
    result = []
    in_ul = False
    in_ol = False
    current_ol_start = 1
    
    for i, line in enumerate(processed_lines):
        stripped = line.strip()
        
        if stripped.startswith('<li>'):
            # Determine if this is an ordered list by checking the original line
            original_line = lines[i] if i < len(lines) else ''
            is_ordered = bool(re.match(r'^\d+\. ', original_line.strip()))
            
            if is_ordered:
                # Extract the number from the original line
                match = re.match(r'^(\d+)\. ', original_line.strip())
                if match:
                    number = int(match.group(1))
                    
                    if not in_ol:
                        if in_ul:
                            result.append('</ul>')
                            in_ul = False
                        # Use the actual number as the start value
                        result.append(f'<ol start="{number}">')
                        in_ol = True
                        current_ol_start = number
                    elif number != current_ol_start:
                        # If the number changes, close current ol and start new one
                        result.append('</ol>')
                        result.append(f'<ol start="{number}">')
                        current_ol_start = number
            elif not in_ul:
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append('<ul>')
                in_ul = True
            result.append(line)
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            elif in_ol:
                result.append('</ol>')
                in_ol = False
            result.append(line)
    
    if in_ul:
        result.append('</ul>')
    elif in_ol:
        result.append('</ol>')
    
    markdown_text = '\n'.join(result)
    
    # Convert paragraphs
    content = markdown_text
    content = re.sub(r'\n\n([^<].*?)\n\n', r'\n\n<p>\1</p>\n\n', content, flags=re.DOTALL)
    
    return content
