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
    # GitHub README URL for TempHist app
    github_readme_url = "https://raw.githubusercontent.com/turnpiece/temphist_app/main/README.md"
    
    try:
        # Fetch README content from GitHub
        response = requests.get(github_readme_url, timeout=10)
        if response.status_code == 200:
            readme_content = response.text
            # Convert markdown to HTML (basic conversion)
            html_content = convert_markdown_to_html(readme_content)
        else:
            html_content = "<p>Unable to load documentation from GitHub. Please check the repository URL.</p>"
    except Exception as e:
        html_content = f"<p>Error loading documentation: {str(e)}</p>"
    
    return render(request, "core/temphist_docs.html", {"content": html_content})

def convert_markdown_to_html(markdown_text):
    """Basic markdown to HTML conversion."""
    # Convert headers
    markdown_text = re.sub(r'^### (.*$)', r'<h3>\1</h3>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^## (.*$)', r'<h2>\1</h2>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^# (.*$)', r'<h1>\1</h1>', markdown_text, flags=re.MULTILINE)
    
    # Convert bold and italic
    markdown_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown_text)
    markdown_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', markdown_text)
    
    # Convert code blocks
    markdown_text = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', markdown_text, flags=re.DOTALL)
    markdown_text = re.sub(r'`(.*?)`', r'<code>\1</code>', markdown_text)
    
    # Convert links
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', markdown_text)
    
    # Convert lists
    markdown_text = re.sub(r'^\* (.*$)', r'<li>\1</li>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^- (.*$)', r'<li>\1</li>', markdown_text, flags=re.MULTILINE)
    
    # Wrap lists in ul tags (basic implementation)
    lines = markdown_text.split('\n')
    in_list = False
    result = []
    
    for line in lines:
        if line.strip().startswith('<li>'):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(line)
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')
    
    # Convert paragraphs
    content = '\n'.join(result)
    content = re.sub(r'\n\n([^<].*?)\n\n', r'\n\n<p>\1</p>\n\n', content, flags=re.DOTALL)
    
    return content
