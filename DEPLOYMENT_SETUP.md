# Deployment Setup Guide - PostgreSQL & CORS Configuration

## Summary
Configured the backend to:
1. **Allow all CORS requests** (for hackathon - no CORS errors)
2. **Support PostgreSQL cloud databases** (with automatic fallback to SQLite)
3. **Allow all hosts** (for easy deployment)

---

## Changes Made

### 1. Django Settings (`kiroween_backend/phantom/settings.py`)

#### CORS Configuration - Allow Everything
```python
# Allow all origins for hackathon
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*']
```

#### Allowed Hosts - Accept All
```python
ALLOWED_HOSTS = ['*']  # Accepts requests from any domain
```

#### Database Configuration - PostgreSQL Support
```python
# Automatically uses PostgreSQL if DATABASE_URL is set
# Falls back to SQLite for local development
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### 2. Environment Variables (`.env`)

Added PostgreSQL configuration options:
```env
# Allow all CORS origins (for hackathon)
CORS_ALLOW_ALL_ORIGINS=True

# PostgreSQL Database URL (leave empty for SQLite)
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### 3. Requirements (`requirements.txt`)

Added PostgreSQL support packages:
```
dj-database-url==2.1.0
psycopg2-binary==2.9.9
```

---

## How to Use

### Option 1: Local Development (SQLite)
**No changes needed!** Just run as usual:
```bash
cd kiroween_backend
python manage.py runserver
```

### Option 2: Cloud PostgreSQL Database

#### Step 1: Install New Dependencies
```bash
cd kiroween_backend
pip install -r requirements.txt
```

#### Step 2: Get Your PostgreSQL Connection String

Choose your cloud provider and get the connection URL:

**Supabase:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Neon:**
```
postgresql://[user]:[password]@[endpoint].neon.tech/[dbname]
```

**Railway:**
```
postgresql://postgres:[password]@containers-us-west-xxx.railway.app:5432/railway
```

**Heroku:**
```
postgres://[user]:[password]@[host]:5432/[dbname]
```

**AWS RDS:**
```
postgresql://[user]:[password]@[instance].region.rds.amazonaws.com:5432/[dbname]
```

#### Step 3: Update `.env` File
```env
# Add your PostgreSQL connection string
DATABASE_URL=postgresql://username:password@host:port/database_name

# Example with Supabase:
# DATABASE_URL=postgresql://postgres:mypassword@db.abcdefghijk.supabase.co:5432/postgres
```

#### Step 4: Run Migrations
```bash
cd kiroween_backend
python manage.py migrate
```

#### Step 5: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

#### Step 6: Run Server
```bash
python manage.py runserver
```

---

## CORS Configuration

### Current Setup (Hackathon Mode)
- ✅ **All origins allowed** - No CORS errors from any domain
- ✅ **All methods allowed** - GET, POST, PUT, DELETE, PATCH, etc.
- ✅ **All headers allowed** - Any custom headers work
- ✅ **Credentials allowed** - Cookies and auth headers work

### For Production (After Hackathon)

Update `.env`:
```env
# Disable allow-all
CORS_ALLOW_ALL_ORIGINS=False

# Specify allowed origins
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Database Migration from SQLite to PostgreSQL

If you have existing data in SQLite and want to move to PostgreSQL:

### Method 1: Using Django's dumpdata/loaddata

1. **Export data from SQLite:**
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data.json
```

2. **Update `.env` with PostgreSQL URL**

3. **Run migrations on PostgreSQL:**
```bash
python manage.py migrate
```

4. **Import data:**
```bash
python manage.py loaddata data.json
```

### Method 2: Fresh Start (Recommended for Hackathon)

1. **Update `.env` with PostgreSQL URL**

2. **Run migrations:**
```bash
python manage.py migrate
```

3. **Create new superuser:**
```bash
python manage.py createsuperuser
```

4. **Create categories:**
```bash
python manage.py shell
```
```python
from scheduler.models import Category

categories = [
    {'name': 'Exam', 'priority_level': 5, 'color': '#FF5252'},
    {'name': 'Study', 'priority_level': 4, 'color': '#4CAF50'},
    {'name': 'Gym', 'priority_level': 3, 'color': '#2196F3'},
    {'name': 'Social', 'priority_level': 2, 'color': '#FFC107'},
    {'name': 'Gaming', 'priority_level': 1, 'color': '#9C27B0'},
]

for cat in categories:
    Category.objects.get_or_create(**cat)
```

---

## Popular Cloud PostgreSQL Providers

### 1. **Supabase** (Recommended for Hackathons)
- ✅ Free tier available
- ✅ Easy setup
- ✅ Good performance
- 🔗 https://supabase.com

### 2. **Neon**
- ✅ Generous free tier
- ✅ Serverless PostgreSQL
- ✅ Fast cold starts
- 🔗 https://neon.tech

### 3. **Railway**
- ✅ Simple deployment
- ✅ Free tier
- ✅ Great for hackathons
- 🔗 https://railway.app

### 4. **Heroku**
- ✅ Easy PostgreSQL addon
- ✅ Free tier (limited)
- ✅ Well documented
- 🔗 https://heroku.com

### 5. **AWS RDS**
- ✅ Production-ready
- ⚠️ More complex setup
- ⚠️ Paid service
- 🔗 https://aws.amazon.com/rds/

---

## Troubleshooting

### CORS Errors Still Occurring?

1. **Check if corsheaders is in INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]
```

2. **Check middleware order:**
```python
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```

3. **Restart the server:**
```bash
# Stop the server (Ctrl+C)
# Start again
python manage.py runserver
```

### PostgreSQL Connection Errors?

1. **Check connection string format:**
```
postgresql://username:password@host:port/database
```

2. **Verify credentials:**
- Username is correct
- Password is correct (no special characters unescaped)
- Host and port are accessible

3. **Test connection:**
```bash
psql "postgresql://username:password@host:port/database"
```

4. **Check firewall/security groups:**
- Database allows connections from your IP
- Port 5432 is open

### Migration Errors?

1. **Reset migrations (if needed):**
```bash
# Delete all migration files except __init__.py
# Then:
python manage.py makemigrations
python manage.py migrate
```

2. **Check database permissions:**
- User has CREATE TABLE permissions
- User has ALTER TABLE permissions

---

## Security Notes (For Production)

⚠️ **Current configuration is for hackathon/development only!**

For production deployment:

1. **Set `DEBUG=False`** in `.env`
2. **Set `CORS_ALLOW_ALL_ORIGINS=False`**
3. **Specify exact `ALLOWED_HOSTS`**
4. **Use strong `SECRET_KEY`**
5. **Enable HTTPS**
6. **Use environment-specific `.env` files**
7. **Set up proper database backups**
8. **Configure rate limiting**
9. **Enable security headers**
10. **Use a reverse proxy (nginx)**

---

## Quick Start Commands

### Local Development (SQLite)
```bash
cd kiroween_backend
python manage.py runserver
```

### Cloud Database (PostgreSQL)
```bash
cd kiroween_backend
pip install -r requirements.txt
# Update .env with DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Check Current Database
```bash
python manage.py shell
```
```python
from django.conf import settings
print(settings.DATABASES['default'])
```

---

## Environment Variables Summary

```env
# Security
SECRET_KEY=your-secret-key
DEBUG=True

# Hosts & CORS (Hackathon Mode)
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True

# Database (Optional - leave empty for SQLite)
DATABASE_URL=postgresql://user:pass@host:port/db

# API Keys
GEMINI_API_KEY=your-gemini-key

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Success Checklist

- ✅ No CORS errors from any origin
- ✅ Backend accepts requests from any host
- ✅ PostgreSQL connection working (if configured)
- ✅ Migrations applied successfully
- ✅ API endpoints accessible
- ✅ Authentication working
- ✅ Frontend can communicate with backend

---

## Support

If you encounter issues:

1. Check the logs: `kiroween_backend/logs/phantom.log`
2. Verify environment variables are loaded
3. Test database connection
4. Check Django settings are correct
5. Restart the server

For PostgreSQL-specific issues, check the provider's documentation.
