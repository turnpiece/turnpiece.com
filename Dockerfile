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

# Build Tailwind CSS
COPY theme/package.json theme/package-lock.json* ./theme/
COPY theme/static_src ./theme/static_src/
RUN cd theme && npm install && npm run build-css

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "turnpiece.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
