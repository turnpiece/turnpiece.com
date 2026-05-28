from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from .forms import ContactForm
from projects.views import PROJECTS_DATA
import requests
import re
import time


def send_contact_email(form_data, subject_prefix, recipient_email):
    """Helper function to send contact form emails."""
    email = EmailMessage(
        subject=f"{subject_prefix} from {form_data['name']}",
        body=f"Name: {form_data['name']}\nEmail: {form_data['email']}\n\nMessage:\n{form_data['message']}",
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
        reply_to=[form_data['email']],
    )
    email.send()


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
    
    # Get all projects from centralized source
    projects = list(PROJECTS_DATA.values())
    for project in projects:
        for repo in project['repositories']:
            repo['project_slug'] = project['slug']

    return render(request, "core/home.html", {
        "form": form, 
        "submitted": submitted, 
        "error_message": error_message,
        "projects": projects
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
