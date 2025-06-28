# turnpiece.com

The official website for Turnpiece, built with Django.

## Overview

Turnpiece.com is a Django-based website featuring a clean, modern design with a centered logo homepage and a support contact form. The site is designed to be scalable and maintainable with a reusable header component and modular structure.

## Features

- **Home Page**: Clean, centered logo design with fade-in animation
- **Support Page**: Professional contact form with validation and success feedback
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Clean typography and professional styling
- **SVG/PNG Logo Support**: Optimized logo display with SVG as primary, PNG as fallback
- **Reusable Components**: Base template with header for consistent branding

## Project Structure

```
turnpiece.com/
├── turnpiece/                 # Django project settings
│   ├── settings.py           # Main Django configuration
│   ├── urls.py               # Project URL routing
│   └── wsgi.py               # WSGI application
├── core/                     # Main Django app
│   ├── views.py              # View functions (home, support, contact)
│   ├── urls.py               # App URL patterns
│   ├── forms.py              # Contact form definition
│   └── templates/core/       # App-specific templates
│       ├── home.html         # Home page template
│       └── support.html      # Support page template
├── templates/                # Global templates
│   └── base.html             # Base template with header
├── static/                   # Static files
│   └── assets/               # Logo files
│       ├── tp-logo-white-transparent-fixed.svg
│       └── tp-logo-white-transparent-fixed.png
├── manage.py                 # Django management script
└── README.md                 # This file
```

## Technology Stack

- **Backend**: Django 5.2.3
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development)
- **Static Files**: Django's built-in static file handling
- **Email**: Django's email backend (configurable)

## Local Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd turnpiece.com
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install django
   ```

4. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

5. **Start the development server**

   ```bash
   python manage.py runserver
   ```

6. **Visit the site**
   - Home page: http://127.0.0.1:8000/
   - Support page: http://127.0.0.1:8000/support/

### Development Commands

```bash
# Run the development server
python manage.py runserver

# Run on a different port
python manage.py runserver 8001

# Check for issues
python manage.py check

# Create database migrations (if models are added)
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser
```

## Configuration

### Email Settings

To enable email functionality for the support form, update `turnpiece/settings.py`:

```python
# Email configuration (example for Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Environment Variables

For production, consider using environment variables for sensitive settings:

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

## Deployment

### Production Considerations

1. **Set DEBUG = False** in settings.py
2. **Configure a production database** (PostgreSQL recommended)
3. **Set up proper email backend**
4. **Configure static file serving** (nginx, AWS S3, etc.)
5. **Use environment variables** for sensitive settings
6. **Set up HTTPS** with SSL certificates

### Recommended Stack

- **Web Server**: nginx
- **Application Server**: Gunicorn
- **Database**: PostgreSQL
- **Static Files**: AWS S3 or nginx
- **Email**: SendGrid, Mailgun, or AWS SES

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally
4. Submit a pull request

## License

[Add your license information here]
