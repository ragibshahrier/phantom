# Phantom Scheduler - Quick Start Guide

Get Phantom Scheduler up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- Redis (for task queue)

## Installation Steps

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd phantom-scheduler

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set at minimum:
# - SECRET_KEY (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# - GEMINI_API_KEY (get from: https://makersuite.google.com/app/apikey)
```

### 3. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Populate default categories
python manage.py populate_categories

# Create admin user (optional)
python manage.py createsuperuser
```

### 4. Start Services

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Redis (if not running as service):**
```bash
redis-server
```

**Terminal 3 - Celery Worker:**
```bash
celery -A phantom worker -l info
```

### 5. Test the API

Visit http://localhost:8000/api/docs/ to see the interactive API documentation.

## First API Call

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "name": "Test User", "password": "testpass123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

Save the `access` token from the response.

### 3. Create an Event

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"message": "Schedule a study session tomorrow at 2pm for 2 hours"}'
```

## What's Next?

- **Full Documentation**: See [README.md](README.md)
- **API Reference**: Visit http://localhost:8000/api/docs/
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Common Issues

### Redis Connection Error
**Problem**: `Error 111 connecting to localhost:6379. Connection refused.`

**Solution**: Start Redis server:
```bash
# Windows (if installed via Chocolatey)
redis-server

# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

### Gemini API Error
**Problem**: `Invalid API key` or `API key not found`

**Solution**: 
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`
3. Restart Django server

### Migration Error
**Problem**: `No such table: scheduler_user`

**Solution**: Run migrations:
```bash
python manage.py migrate
python manage.py populate_categories
```

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Open an issue on GitHub

---

*"Welcome aboard! I am Phantom, your Victorian Ghost Butler. Let us begin organizing your schedule with the utmost efficiency."*
