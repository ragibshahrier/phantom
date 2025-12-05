"""
Management command to populate default categories.
"""
from django.core.management.base import BaseCommand
from scheduler.models import Category


class Command(BaseCommand):
    help = 'Populate default event categories with priority levels'

    def handle(self, *args, **options):
        """Create default categories if they don't exist."""
        default_categories = [
            {'name': 'Exam', 'priority_level': 5, 'color': '#FF0000', 'description': 'Exams and tests'},
            {'name': 'Study', 'priority_level': 4, 'color': '#FFA500', 'description': 'Study sessions'},
            {'name': 'Gym', 'priority_level': 3, 'color': '#00FF00', 'description': 'Gym and fitness activities'},
            {'name': 'Social', 'priority_level': 2, 'color': '#0000FF', 'description': 'Social events and gatherings'},
            {'name': 'Gaming', 'priority_level': 1, 'color': '#800080', 'description': 'Gaming and entertainment'},
        ]

        created_count = 0
        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'priority_level': category_data['priority_level'],
                    'color': category_data['color'],
                    'description': category_data['description'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name} (Priority: {category.priority_level})')
                )
            else:
                self.stdout.write(f'Category already exists: {category.name}')

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} categories'))
        else:
            self.stdout.write('All default categories already exist')
