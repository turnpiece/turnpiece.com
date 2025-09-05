from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from .forms import ContactForm
import requests
import re
import time


def send_contact_email(form_data, subject_prefix, recipient_email):
    """Helper function to send contact form emails."""
    send_mail(
        subject=f"{subject_prefix} from {form_data['name']}",
        message=f"Name: {form_data['name']}\nEmail: {form_data['email']}\n\nMessage:\n{form_data['message']}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient_email],
        reply_to=[form_data['email']],
    )


def check_rate_limit(request, limit=3, window=300):
    """Check if user has exceeded rate limit (3 submissions per 5 minutes)."""
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f"contact_form_rate_limit_{ip_address}"
    
    # Get current submissions count
    submissions = cache.get(cache_key, [])
    current_time = time.time()
    
    # Remove old submissions outside the window
    submissions = [timestamp for timestamp in submissions if current_time - timestamp < window]
    
    # Check if limit exceeded
    if len(submissions) >= limit:
        return False
    
    # Add current submission
    submissions.append(current_time)
    cache.set(cache_key, submissions, window)
    return True


def handle_contact_form(request, template_name, success_redirect=None):
    """Helper function to handle contact form submission logic."""
    submitted = False
    error_message = None
    
    if request.method == "POST":
        # Check rate limit first
        if not check_rate_limit(request):
            error_message = "Too many submissions. Please wait 5 minutes before trying again."
            form = ContactForm(request.POST)
        else:
            form = ContactForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                return cd, True, ContactForm(), None  # Return form data, submitted status, cleared form, and no error
    else:
        form = ContactForm()
    
    return None, submitted, form, error_message

def home_view(request):
    """Home page view with hero, projects, and contact form."""
    form_data, submitted, form, error_message = handle_contact_form(request, "core/home.html")
    
    if form_data:  # Form was submitted and valid
        send_contact_email(form_data, "Turnpiece.com contact message", settings.CONTACT_EMAIL)
        submitted = True
    
    return render(request, "core/home.html", {
        "form": form, 
        "submitted": submitted, 
        "error_message": error_message
    })

def support_view(request):
    """Support page view with contact form."""
    form_data, submitted, form, error_message = handle_contact_form(request, "core/support.html")
    
    if form_data:  # Form was submitted and valid
        send_contact_email(form_data, "Turnpiece.com support request", settings.SUPPORT_EMAIL)
        submitted = True
    
    return render(request, "core/support.html", {
        "form": form, 
        "submitted": submitted, 
        "error_message": error_message
    })

def contact_view(request):
    """Contact page view with contact form."""
    form_data, submitted, form, error_message = handle_contact_form(request, "core/contact.html")
    
    if form_data:  # Form was submitted and valid
        send_contact_email(form_data, "Support message", settings.CONTACT_EMAIL)
        submitted = True
    
    return render(request, "core/contact.html", {
        "form": form, 
        "submitted": submitted, 
        "error_message": error_message
    })

def temphist_docs_view(request):
    """TempHist app documentation page."""
    # Repository information with custom project details
    repo_info = {
        'name': 'TempHist',
        'description': 'Flutter application for temperature visualization',
        'github_url': 'https://github.com/turnpiece/temphist_app',
        'readme_url': 'https://raw.githubusercontent.com/turnpiece/temphist_app/main/README.md',
        # Custom project information
        'logo_svg': 'assets/temphist-logo.svg',  # SVG logo
        'logo_png': 'assets/temphist-logo.png',  # PNG fallback
        'screenshots': [
            {
                'src': 'assets/TempHist-iPhone-screenshot.png',
                'alt': 'TempHist main screen showing temperature chart',
                'caption': 'Main temperature visualization screen'
            }
        ],
        'custom_description': 'TempHist is a Flutter application that visualizes historical average temperatures by year using horizontal bar charts. Built with the graphic package, it provides an intuitive way to explore temperature trends over time.',
        'tech_stack': ['Flutter', 'Dart', 'Graphic Package', 'Firebase'],
        'features': [
            'Horizontal bar chart visualization',
            'Historical temperature data display',
            'Cross-platform (iOS, Android, Web)',
            'Firebase backend integration'
        ]
    }
    
    try:
        # Fetch README content from GitHub
        response = requests.get(repo_info['readme_url'], timeout=10)
        if response.status_code == 200:
            readme_content = response.text
            # Convert markdown to HTML (basic conversion)
            html_content = convert_markdown_to_html(readme_content)
        else:
            html_content = "<p>Unable to load documentation from GitHub. Please check the repository URL.</p>"
    except Exception as e:
        html_content = f"<p>Error loading documentation: {str(e)}</p>"
    
    return render(request, "core/github_docs.html", {
        "content": html_content,
        "repo_info": repo_info
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
