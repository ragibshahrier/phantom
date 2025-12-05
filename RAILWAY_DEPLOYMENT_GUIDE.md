# Railway Deployment Guide - Django Backend

## Overview
This guide will help you deploy the Django backend from a monorepo (frontend + backend) to Railway.

---

## Prerequisites

✅ GitHub repository with both frontend and backend
✅ Railway account (sign up at https://railway.app)
✅ PostgreSQL database already created in Railway (you have this)

---

## Files Created for Deployment

### 1. `kiroween_backend/railway.json`
Railway configuration file that tells Railway how to build and deploy.

### 2. `kiroween_backend/Procfile`
Tells Railway how to start the application.

### 3. `kiroween_backend/runtime.txt`
Specifies Python version.

### 4. Updated `requirements.txt`
Added production dependencies:
- `gunicorn` - Production WSGI server
- `whitenoise` - Static file serving

### 5. Updated `settings.py`
- Added WhiteNoise middleware for static files
- Configured STATIC_ROOT and STATICFILES_STORAGE

---

## Step-by-Step Deployment

### Step 1: Commit and Push Changes

```bash
# Make sure you're in the root directory
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Create New Project in Railway

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your repository

### Step 3: Configure Root Directory

⚠️ **IMPORTANT**: Since your backend is in a subdirectory, you need to tell Railway:

1. After selecting your repo, Railway will create a service
2. Click on the service
3. Go to **Settings** tab
4. Find **"Root Directory"** setting
5. Set it to: `kiroween_backend`
6. Click **Save**

### Step 4: Add Environment Variables

In Railway, go to **Variables** tab and add these:

#### Required Variables

```env
# Django Secret Key (generate a new one for production)
SECRET_KEY=your-production-secret-key-here

# Debug Mode (set to False for production)
DEBUG=False

# Database URL (Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Allowed Hosts (Railway will provide the domain)
ALLOWED_HOSTS=*.railway.app,yourdomain.com

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True

# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# Celery/Redis (if you're using it)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### How to Get DATABASE_URL

If you already have a PostgreSQL database in Railway:

1. Click on your PostgreSQL service
2. Go to **Variables** tab
3. Copy the `DATABASE_URL` value
4. In your Django service, add variable: `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`

Or simply reference it: `${{Postgres.DATABASE_URL}}`

### Step 5: Generate Production Secret Key

Run this locally to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY` in Railway.

### Step 6: Deploy

1. Railway will automatically deploy after you save the variables
2. Or click **"Deploy"** button manually
3. Watch the build logs in the **Deployments** tab

### Step 7: Run Migrations

After first deployment, you need to run migrations:

**Option A: Using Railway CLI**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser (optional)
railway run python manage.py createsuperuser
```

**Option B: Using Railway Dashboard**
1. Go to your service
2. Click **Settings** → **Deploy**
3. Add to **Build Command**:
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

### Step 8: Setup Categories

After migrations, create default categories:

```bash
railway run python manage.py shell
```

Then in the shell:
```python
from scheduler.models import Category

categories = [
    {'name': 'Exam', 'priority_level': 5, 'color': '#FF5252', 'description': 'Exams, tests, and quizzes'},
    {'name': 'Study', 'priority_level': 4, 'color': '#4CAF50', 'description': 'Study sessions'},
    {'name': 'Gym', 'priority_level': 3, 'color': '#2196F3', 'description': 'Workouts'},
    {'name': 'Social', 'priority_level': 2, 'color': '#FFC107', 'description': 'Social events'},
    {'name': 'Gaming', 'priority_level': 1, 'color': '#9C27B0', 'description': 'Gaming'},
]

for cat in categories:
    Category.objects.get_or_create(**cat)
```

### Step 9: Get Your Deployment URL

1. Go to **Settings** tab
2. Find **Domains** section
3. Railway provides a domain like: `your-app.railway.app`
4. You can also add a custom domain

### Step 10: Test Your API

```bash
# Test health check
curl https://your-app.railway.app/api/

# Test registration
curl -X POST https://your-app.railway.app/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","name":"Test User","password":"testpass123","password_confirm":"testpass123"}'
```

---

## Environment Variables Reference

### Essential Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-xyz...` |
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | PostgreSQL connection | `${{Postgres.DATABASE_URL}}` |
| `ALLOWED_HOSTS` | Allowed domains | `*.railway.app` |
| `GEMINI_API_KEY` | Google Gemini API | `AIzaSy...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS | `True` |
| `JWT_ACCESS_TOKEN_LIFETIME` | JWT access token lifetime (minutes) | `15` |
| `JWT_REFRESH_TOKEN_LIFETIME` | JWT refresh token lifetime (minutes) | `10080` |

---

## Troubleshooting

### Build Fails

**Error**: `No module named 'gunicorn'`
- **Solution**: Make sure `gunicorn` is in `requirements.txt`

**Error**: `Could not find requirements.txt`
- **Solution**: Check that Root Directory is set to `kiroween_backend`

### Database Connection Fails

**Error**: `relation "scheduler_user" does not exist`
- **Solution**: Run migrations: `railway run python manage.py migrate`

**Error**: `could not connect to server`
- **Solution**: Check `DATABASE_URL` is correctly set to `${{Postgres.DATABASE_URL}}`

### Static Files Not Loading

**Error**: 404 on `/static/` files
- **Solution**: Run `python manage.py collectstatic` (should be in build command)
- **Check**: WhiteNoise is in MIDDLEWARE

### CORS Errors

**Error**: CORS policy blocking requests
- **Solution**: Set `CORS_ALLOW_ALL_ORIGINS=True` in environment variables
- **Check**: `corsheaders` is in INSTALLED_APPS and MIDDLEWARE

### Application Won't Start

**Error**: `Web process failed to bind to $PORT`
- **Solution**: Check Procfile uses `--bind 0.0.0.0:$PORT`

**Error**: `ModuleNotFoundError`
- **Solution**: Check all dependencies are in `requirements.txt`

---

## Post-Deployment Checklist

- [ ] Migrations run successfully
- [ ] Categories created
- [ ] Superuser created (optional)
- [ ] API endpoints accessible
- [ ] Registration works
- [ ] Login works
- [ ] Chat endpoint works
- [ ] Events can be created
- [ ] CORS configured correctly
- [ ] Custom domain added (optional)

---

## Connecting Frontend to Backend

Once deployed, update your frontend's API URL:

### In `phantom_frontend/config/api.ts` (or similar):

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-app.railway.app';
```

### Or in `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

---

## Monitoring and Logs

### View Logs

1. Go to your service in Railway
2. Click **Deployments** tab
3. Click on a deployment
4. View **Build Logs** and **Deploy Logs**

### Monitor Performance

1. Go to **Metrics** tab
2. View CPU, Memory, Network usage

### Set Up Alerts

1. Go to **Settings** → **Notifications**
2. Configure deployment notifications

---

## Scaling

### Vertical Scaling (More Resources)

1. Go to **Settings** → **Resources**
2. Upgrade your plan for more CPU/RAM

### Horizontal Scaling (Multiple Instances)

Railway Pro plan supports multiple replicas:
1. Go to **Settings** → **Replicas**
2. Increase replica count

---

## Custom Domain Setup

1. Go to **Settings** → **Domains**
2. Click **Add Domain**
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Add the CNAME record to your DNS:
   - Type: `CNAME`
   - Name: `api` (or `@` for root)
   - Value: `your-app.railway.app`
5. Wait for DNS propagation (5-30 minutes)
6. Update `ALLOWED_HOSTS` to include your domain

---

## Security Best Practices

### For Production:

1. **Set DEBUG=False**
   ```env
   DEBUG=False
   ```

2. **Use Strong SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Restrict ALLOWED_HOSTS**
   ```env
   ALLOWED_HOSTS=your-app.railway.app,yourdomain.com
   ```

4. **Restrict CORS** (after testing)
   ```env
   CORS_ALLOW_ALL_ORIGINS=False
   CORS_ALLOWED_ORIGINS=https://yourfrontend.com
   ```

5. **Use HTTPS Only**
   - Railway provides HTTPS by default
   - Enforce in Django:
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

---

## Backup and Restore

### Backup Database

```bash
# Using Railway CLI
railway run pg_dump $DATABASE_URL > backup.sql
```

### Restore Database

```bash
railway run psql $DATABASE_URL < backup.sql
```

---

## Cost Optimization

### Free Tier Limits

- $5 free credit per month
- Sleeps after 30 minutes of inactivity
- 500 hours of usage per month

### Tips to Stay in Free Tier

1. Use sleep mode for non-critical apps
2. Optimize database queries
3. Use caching (Redis)
4. Minimize build times

---

## Quick Commands Reference

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Open shell
railway run python manage.py shell

# View logs
railway logs

# Open in browser
railway open
```

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Django Docs: https://docs.djangoproject.com

---

## Summary

✅ **Files Created**:
- `railway.json` - Railway configuration
- `Procfile` - Start command
- `runtime.txt` - Python version
- Updated `requirements.txt` - Added gunicorn, whitenoise
- Updated `settings.py` - Production settings

✅ **Deployment Steps**:
1. Push code to GitHub
2. Create Railway project
3. Set root directory to `kiroween_backend`
4. Add environment variables
5. Deploy
6. Run migrations
7. Create categories
8. Test API

✅ **Your Backend URL**: `https://your-app.railway.app`

Your Django backend is now ready for production deployment on Railway! 🚀
