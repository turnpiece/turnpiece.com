FROM python:3.12-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node dependencies (separate layer for caching)
COPY theme/package.json theme/package-lock.json* ./theme/
RUN cd theme && npm install

# Copy all application code (templates must exist before Tailwind scans content)
COPY . .

# Build Tailwind CSS (scans templates for used classes)
RUN cd theme && npm run build-css

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD gunicorn turnpiece.wsgi:application --bind 0.0.0.0:$PORT --workers 2
