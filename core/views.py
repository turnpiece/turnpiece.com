from django.shortcuts import render
from django.core.mail import send_mail
from .forms import ContactForm
import requests
import re

def home_view(request):
    """Home page view with centered logo."""
    return render(request, "core/home.html")

def support_view(request):
    """Support page view with contact form."""
    submitted = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Replace below with actual email config
            send_mail(
                subject=f"Support request from {cd['name']}",
                message=cd['message'],
                from_email=cd['email'],
                recipient_list=["support@turnpiece.com"],
            )
            submitted = True
            form = ContactForm()  # clear form after submission
    else:
        form = ContactForm()
    return render(request, "core/support.html", {"form": form, "submitted": submitted})

def contact_view(request):
    submitted = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Replace below with actual email config
            send_mail(
                subject=f"Support message from {cd['name']}",
                message=cd['message'],
                from_email=cd['email'],
                recipient_list=["you@example.com"],
            )
            submitted = True
            form = ContactForm()  # clear form after submission
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form, "submitted": submitted})

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
