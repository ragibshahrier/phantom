# Railway Deployment Quick Checklist

## Before Deployment

- [ ] Code pushed to GitHub
- [ ] All changes committed
- [ ] `.env` file NOT committed (in .gitignore)

## Railway Setup

### 1. Create Project
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository

### 2. Configure Service
- [ ] Set **Root Directory** to: `kiroween_backend`
- [ ] Save settings

### 3. Add Environment Variables

Copy these to Railway Variables tab:

```env
SECRET_KEY=<generate-new-key>
DEBUG=False
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_HOSTS=*.railway.app
CORS_ALLOW_ALL_ORIGINS=True
GEMINI_API_KEY=<your-api-key>
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### 4. Generate Secret Key

Run locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Deploy
- [ ] Click "Deploy" or wait for auto-deploy
- [ ] Watch build logs

### 6. Run Migrations

Install Railway CLI:
```bash
npm i -g @railway/cli
railway login
railway link
railway run python manage.py migrate
```

### 7. Create Categories

```bash
railway run python manage.py shell
```

Then:
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

### 8. Test API

```bash
curl https://your-app.railway.app/api/
```

## Post-Deployment

- [ ] API accessible
- [ ] Registration works
- [ ] Login works
- [ ] Events can be created
- [ ] Update frontend API URL

## Your Deployment URL

```
https://your-app.railway.app
```

## Common Issues

**Build fails**: Check Root Directory = `kiroween_backend`
**Database error**: Run migrations
**CORS error**: Set `CORS_ALLOW_ALL_ORIGINS=True`
**Static files 404**: Check WhiteNoise in MIDDLEWARE

## Quick Commands

```bash
# View logs
railway logs

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Open shell
railway run python manage.py shell
```

Done! ✅
