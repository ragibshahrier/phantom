# Phantom Scheduler - Deployment Guide

This guide provides detailed instructions for deploying Phantom Scheduler to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Production Configuration](#production-configuration)
- [Database Setup](#database-setup)
- [Web Server Configuration](#web-server-configuration)
- [Deployment Options](#deployment-options)
- [Post-Deployment](#post-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows Server
- **Python**: 3.10 or higher
- **Database**: PostgreSQL 14+ (recommended for production)
- **Redis**: 6.0+ (for Celery task queue)
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Storage**: Minimum 10GB available space

### Required Services

1. **PostgreSQL Database**
   - For persistent data storage
   - Recommended for production (SQLite is only for development)

2. **Redis Server**
   - For Celery task queue
   - For caching (optional but recommended)

3. **Web Server**
   - Nginx or Apache (recommended)
   - For serving static files and reverse proxy

4. **WSGI Server**
   - Gunicorn or uWSGI
   - For running Django application

## Production Configuration

### 1. Environment Variables

Create a production `.env` file with secure values:

```env
# Django Settings
SECRET_KEY=<generate-strong-random-key-here>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://phantom_user:secure_password@localhost:5432/phantom_prod

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# Google Gemini API
GEMINI_API_KEY=your-production-gemini-api-key

# Google Calendar API
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Generate Secret Key

Generate a secure Django secret key:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Security Settings

Update `phantom/settings.py` for production:

```python
# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE phantom_prod;
CREATE USER phantom_user WITH PASSWORD 'secure_password';
ALTER ROLE phantom_user SET client_encoding TO 'utf8';
ALTER ROLE phantom_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE phantom_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE phantom_prod TO phantom_user;

# Exit PostgreSQL
\q
```

### Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Populate default categories
python manage.py populate_categories

# Create superuser
python manage.py createsuperuser
```

### Database Backups

Set up automated backups:

```bash
# Create backup script
cat > /usr/local/bin/backup-phantom-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/phantom"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U phantom_user phantom_prod | gzip > $BACKUP_DIR/phantom_backup_$TIMESTAMP.sql.gz
# Keep only last 30 days of backups
find $BACKUP_DIR -name "phantom_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup-phantom-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-phantom-db.sh") | crontab -
```

## Web Server Configuration

### Gunicorn Setup

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn configuration**
   
   Create `gunicorn_config.py`:
   ```python
   import multiprocessing
   
   bind = "127.0.0.1:8000"
   workers = multiprocessing.cpu_count() * 2 + 1
   worker_class = "sync"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 50
   timeout = 30
   keepalive = 2
   
   # Logging
   accesslog = "/var/log/phantom/gunicorn-access.log"
   errorlog = "/var/log/phantom/gunicorn-error.log"
   loglevel = "info"
   
   # Process naming
   proc_name = "phantom-scheduler"
   
   # Server mechanics
   daemon = False
   pidfile = "/var/run/phantom/gunicorn.pid"
   user = "www-data"
   group = "www-data"
   ```

3. **Create systemd service**
   
   Create `/etc/systemd/system/phantom.service`:
   ```ini
   [Unit]
   Description=Phantom Scheduler Gunicorn daemon
   After=network.target
   
   [Service]
   Type=notify
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/phantom-scheduler
   Environment="PATH=/var/www/phantom-scheduler/venv/bin"
   EnvironmentFile=/var/www/phantom-scheduler/.env
   ExecStart=/var/www/phantom-scheduler/venv/bin/gunicorn \
             --config /var/www/phantom-scheduler/gunicorn_config.py \
             phantom.wsgi:application
   ExecReload=/bin/kill -s HUP $MAINPID
   KillMode=mixed
   TimeoutStopSec=5
   PrivateTmp=true
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Gunicorn service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start phantom
   sudo systemctl enable phantom
   sudo systemctl status phantom
   ```

### Celery Setup

1. **Create Celery systemd service**
   
   Create `/etc/systemd/system/phantom-celery.service`:
   ```ini
   [Unit]
   Description=Phantom Scheduler Celery Worker
   After=network.target redis.service
   
   [Service]
   Type=forking
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/phantom-scheduler
   Environment="PATH=/var/www/phantom-scheduler/venv/bin"
   EnvironmentFile=/var/www/phantom-scheduler/.env
   ExecStart=/var/www/phantom-scheduler/venv/bin/celery -A phantom worker \
             --loglevel=info \
             --logfile=/var/log/phantom/celery.log \
             --pidfile=/var/run/phantom/celery.pid
   ExecStop=/bin/kill -s TERM $MAINPID
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Start Celery service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start phantom-celery
   sudo systemctl enable phantom-celery
   sudo systemctl status phantom-celery
   ```

### Nginx Configuration

1. **Install Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **Create Nginx configuration**
   
   Create `/etc/nginx/sites-available/phantom`:
   ```nginx
   upstream phantom_app {
       server 127.0.0.1:8000 fail_timeout=0;
   }
   
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       # Redirect HTTP to HTTPS
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name yourdomain.com www.yourdomain.com;
       
       # SSL Configuration
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
       ssl_prefer_server_ciphers on;
       
       # Security headers
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
       add_header X-Frame-Options "DENY" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header X-XSS-Protection "1; mode=block" always;
       
       # Logging
       access_log /var/log/nginx/phantom-access.log;
       error_log /var/log/nginx/phantom-error.log;
       
       # Max upload size
       client_max_body_size 10M;
       
       # Static files
       location /static/ {
           alias /var/www/phantom-scheduler/staticfiles/;
           expires 30d;
           add_header Cache-Control "public, immutable";
       }
       
       # Media files
       location /media/ {
           alias /var/www/phantom-scheduler/media/;
           expires 7d;
       }
       
       # API endpoints
       location / {
           proxy_pass http://phantom_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_redirect off;
           
           # Timeouts
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }
   }
   ```

3. **Enable site and restart Nginx**
   ```bash
   sudo ln -s /etc/nginx/sites-available/phantom /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

## Deployment Options

### Option 1: Manual Deployment

```bash
# 1. Clone repository
cd /var/www
sudo git clone <repository-url> phantom-scheduler
cd phantom-scheduler

# 2. Set up virtual environment
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install gunicorn

# 4. Configure environment
sudo cp .env.example .env
sudo nano .env  # Edit with production values

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Run migrations
python manage.py migrate
python manage.py populate_categories

# 7. Create superuser
python manage.py createsuperuser

# 8. Set permissions
sudo chown -R www-data:www-data /var/www/phantom-scheduler
sudo chmod -R 755 /var/www/phantom-scheduler

# 9. Start services
sudo systemctl start phantom
sudo systemctl start phantom-celery
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.10-slim
   
   # Set environment variables
   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1
   
   # Set work directory
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       postgresql-client \
       && rm -rf /var/lib/apt/lists/*
   
   # Install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   RUN pip install gunicorn
   
   # Copy project
   COPY . .
   
   # Collect static files
   RUN python manage.py collectstatic --noinput
   
   # Create logs directory
   RUN mkdir -p /app/logs
   
   # Expose port
   EXPOSE 8000
   
   # Run gunicorn
   CMD ["gunicorn", "phantom.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     db:
       image: postgres:14
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         POSTGRES_DB: phantom_prod
         POSTGRES_USER: phantom_user
         POSTGRES_PASSWORD: secure_password
       restart: always
   
     redis:
       image: redis:6-alpine
       restart: always
   
     web:
       build: .
       command: gunicorn phantom.wsgi:application --bind 0.0.0.0:8000 --workers 4
       volumes:
         - .:/app
         - static_volume:/app/staticfiles
       ports:
         - "8000:8000"
       env_file:
         - .env
       depends_on:
         - db
         - redis
       restart: always
   
     celery:
       build: .
       command: celery -A phantom worker -l info
       volumes:
         - .:/app
       env_file:
         - .env
       depends_on:
         - db
         - redis
       restart: always
   
     nginx:
       image: nginx:alpine
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - static_volume:/app/staticfiles
       ports:
         - "80:80"
         - "443:443"
       depends_on:
         - web
       restart: always
   
   volumes:
     postgres_data:
     static_volume:
   ```

3. **Deploy with Docker**
   ```bash
   # Build and start containers
   docker-compose up -d --build
   
   # Run migrations
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py populate_categories
   
   # Create superuser
   docker-compose exec web python manage.py createsuperuser
   
   # View logs
   docker-compose logs -f
   ```

### Option 3: Cloud Platform Deployment

#### Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create phantom-scheduler

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=<your-secret-key>
heroku config:set DEBUG=False
heroku config:set GEMINI_API_KEY=<your-api-key>

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py populate_categories

# Create superuser
heroku run python manage.py createsuperuser
```

#### AWS (Elastic Beanstalk)

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.10 phantom-scheduler

# Create environment
eb create phantom-prod

# Deploy
eb deploy

# Set environment variables
eb setenv SECRET_KEY=<your-secret-key> DEBUG=False GEMINI_API_KEY=<your-api-key>

# Run migrations
eb ssh
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py migrate
python manage.py populate_categories
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Check services status
sudo systemctl status phantom
sudo systemctl status phantom-celery
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Test API
curl https://yourdomain.com/api/schema/
curl https://yourdomain.com/api/docs/

# Check logs
sudo tail -f /var/log/phantom/gunicorn-error.log
sudo tail -f /var/log/phantom/celery.log
sudo tail -f /var/log/nginx/phantom-error.log
```

### 2. Create Initial Data

```bash
# Populate categories
python manage.py populate_categories

# Create superuser
python manage.py createsuperuser
```

### 3. Test Functionality

1. Register a test user
2. Login and obtain JWT tokens
3. Create a test event
4. Verify Google Calendar integration
5. Test natural language processing

## Monitoring and Maintenance

### Application Monitoring

1. **Set up Sentry for error tracking**
   ```bash
   pip install sentry-sdk
   ```
   
   Add to `settings.py`:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[DjangoIntegration()],
       traces_sample_rate=1.0,
       send_default_pii=True
   )
   ```

2. **Set up health check endpoint**
   
   Add to `urls.py`:
   ```python
   from django.http import JsonResponse
   
   def health_check(request):
       return JsonResponse({"status": "healthy"})
   
   urlpatterns = [
       path('health/', health_check),
       # ... other patterns
   ]
   ```

3. **Monitor with Uptime Robot or similar**
   - Set up checks for `/health/` endpoint
   - Configure alerts for downtime

### Log Management

```bash
# View application logs
sudo tail -f /var/log/phantom/phantom.log

# View error logs
sudo tail -f /var/log/phantom/phantom_errors.log

# View Gunicorn logs
sudo tail -f /var/log/phantom/gunicorn-error.log

# View Nginx logs
sudo tail -f /var/log/nginx/phantom-error.log

# Rotate logs (configured in settings.py)
# Logs automatically rotate at 10MB with 5 backups
```

### Database Maintenance

```bash
# Vacuum database (weekly)
sudo -u postgres psql phantom_prod -c "VACUUM ANALYZE;"

# Check database size
sudo -u postgres psql phantom_prod -c "SELECT pg_size_pretty(pg_database_size('phantom_prod'));"

# Clean up old blacklisted tokens (monthly)
python manage.py shell
>>> from scheduler.models import BlacklistedToken
>>> from django.utils import timezone
>>> BlacklistedToken.objects.filter(expires_at__lt=timezone.now()).delete()
```

### Updates and Upgrades

```bash
# Pull latest code
cd /var/www/phantom-scheduler
sudo -u www-data git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart phantom
sudo systemctl restart phantom-celery
```

## Troubleshooting

### Common Issues

#### 1. 502 Bad Gateway

**Cause**: Gunicorn not running or not accessible

**Solution**:
```bash
sudo systemctl status phantom
sudo systemctl restart phantom
sudo tail -f /var/log/phantom/gunicorn-error.log
```

#### 2. Database Connection Errors

**Cause**: PostgreSQL not running or incorrect credentials

**Solution**:
```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"  # List databases
# Check DATABASE_URL in .env
```

#### 3. Static Files Not Loading

**Cause**: Static files not collected or Nginx misconfigured

**Solution**:
```bash
python manage.py collectstatic --noinput
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Celery Tasks Not Processing

**Cause**: Celery worker not running or Redis connection issue

**Solution**:
```bash
sudo systemctl status phantom-celery
sudo systemctl status redis
sudo systemctl restart phantom-celery
```

#### 5. JWT Token Errors

**Cause**: Clock skew or incorrect SECRET_KEY

**Solution**:
```bash
# Sync system time
sudo ntpdate -s time.nist.gov
# Verify SECRET_KEY in .env matches across all servers
```

### Debug Mode

To enable debug mode temporarily (NOT for production):

```bash
# Edit .env
DEBUG=True

# Restart service
sudo systemctl restart phantom

# Remember to disable after debugging
DEBUG=False
sudo systemctl restart phantom
```

### Performance Tuning

1. **Database Connection Pooling**
   ```bash
   pip install psycopg2-binary
   ```
   
   Update `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'CONN_MAX_AGE': 600,  # Connection pooling
       }
   }
   ```

2. **Redis Caching**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **Gunicorn Workers**
   - Adjust workers based on CPU cores: `workers = (2 * cpu_cores) + 1`
   - Monitor memory usage and adjust accordingly

## Security Best Practices

1. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

2. **Regular security audits**
   ```bash
   pip install safety
   safety check
   ```

3. **Firewall configuration**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

4. **Fail2ban for SSH protection**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

5. **Regular backups**
   - Database backups (automated daily)
   - Code backups (Git repository)
   - Configuration backups (.env, nginx configs)

## Support

For deployment issues:
- Check logs first
- Review this guide
- Consult Django deployment documentation
- Open an issue on GitHub

---

**Last Updated**: December 2024
