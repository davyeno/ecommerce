"""
Django command to wait for the database to be available
"""
import time

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entry point for command."""
        self.stdout.write('Create a superuser for database...')
        try:
            User.objects.get(username= 'admin@email.com')
            self.stdout.write(self.style.SUCCESS('Admin superuser already existed!'))
        except User.DoesNotExist:
            User.objects.create_user(username= 'admin@email.com',
                                    email='admin@email.com',
                                    password='admin',
                                    is_staff=True,
                                    is_active=True,
                                    is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Admin superuser created!'))
