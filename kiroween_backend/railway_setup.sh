#!/bin/bash

# Railway Setup Script
# Run this after deploying to Railway

echo "=================================="
echo "Railway Post-Deployment Setup"
echo "=================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "Install it with: npm i -g @railway/cli"
    exit 1
fi

echo "✓ Railway CLI found"

# Login to Railway
echo ""
echo "Step 1: Login to Railway"
railway login

# Link to project
echo ""
echo "Step 2: Link to your project"
railway link

# Run migrations
echo ""
echo "Step 3: Running migrations..."
railway run python manage.py migrate

# Create categories
echo ""
echo "Step 4: Creating default categories..."
railway run python manage.py shell << EOF
from scheduler.models import Category

categories = [
    {'name': 'Exam', 'priority_level': 5, 'color': '#FF5252', 'description': 'Exams, tests, and quizzes'},
    {'name': 'Study', 'priority_level': 4, 'color': '#4CAF50', 'description': 'Study sessions'},
    {'name': 'Gym', 'priority_level': 3, 'color': '#2196F3', 'description': 'Workouts'},
    {'name': 'Social', 'priority_level': 2, 'color': '#FFC107', 'description': 'Social events'},
    {'name': 'Gaming', 'priority_level': 1, 'color': '#9C27B0', 'description': 'Gaming'},
]

for cat in categories:
    obj, created = Category.objects.get_or_create(**cat)
    if created:
        print(f"✓ Created: {obj.name}")
    else:
        print(f"  Exists: {obj.name}")

print("\n✓ Categories setup complete!")
EOF

echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "Your backend is ready at:"
railway open
