# turnpiece.com

The official website for Turnpiece, built with Django.

## Overview

Turnpiece.com is a Django-based website featuring a clean, modern design with a centered logo homepage and a support contact form. The site is designed to be scalable and maintainable with a reusable header component and modular structure.

## Features

- **Home Page**: Clean, centered logo design with fade-in animation
- **Support Page**: Professional contact form with validation and success feedback
- **Contact Forms**: Multiple contact forms with bot prevention and rate limiting
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Clean typography and professional styling
- **SVG/PNG Logo Support**: Optimized logo display with SVG as primary, PNG as fallback
- **Reusable Components**: Base template with header for consistent branding
- **Bot Protection**: Honeypot fields and rate limiting to prevent spam

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

6. **Set up environment variables**

   Copy the example environment file and configure your settings:

   ```bash
   cp env.example .env
   # Edit .env with your actual email addresses and SMTP settings
   ```

7. **Visit the site**
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

The application now uses environment variables for email configuration. Set the following in your `.env` file:

```bash
# Email recipient addresses
CONTACT_EMAIL=paul@turnpiece.com
SUPPORT_EMAIL=support@turnpiece.com

# SMTP configuration (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DJANGO_DEVELOPMENT=False
```

For development, you can set `DJANGO_DEVELOPMENT=True` to use the console email backend instead of SMTP.

### Bot Prevention

The contact forms include several layers of bot protection:

#### 1. Honeypot Field

- **Hidden "website" field** that bots fill but humans can't see
- **Zero impact on user experience** - completely invisible
- **~80-90% effective** against basic bots
- **Automatic rejection** if honeypot is filled

#### 2. Rate Limiting

- **3 submissions per 5 minutes** per IP address
- **Prevents rapid-fire spam** attacks
- **Uses Django cache** for efficient storage
- **~95% effective** against automated spam

#### 3. Form Validation

- **Standard Django form validation** (email format, required fields)
- **Input sanitization** and validation
- **User-friendly error messages**

#### Configuration

- **Rate Limit**: 3 submissions per IP per 5 minutes
- **Honeypot Field**: `website` (completely hidden)
- **Storage**: Django cache system
- **Monitoring**: Check Django logs for "Bot detected" errors

#### Testing Bot Prevention

1. **Honeypot**: Fill the hidden website field and submit
2. **Rate Limiting**: Submit 4+ forms quickly from same IP
3. **Form Validation**: Submit invalid email addresses

#### Advanced Options (If Needed)

If basic measures aren't sufficient, you can add:

- **reCaptcha v3** (invisible, ~99% effective)
- **Time-based validation** (check form fill speed)
- **IP blacklisting** (block known spam IPs)

### Environment Variables

The application uses environment variables for sensitive settings. Key variables include:

```bash
# Django core settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email configuration
CONTACT_EMAIL=paul@turnpiece.com
SUPPORT_EMAIL=support@turnpiece.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
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
