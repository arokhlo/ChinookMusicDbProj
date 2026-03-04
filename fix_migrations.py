# fix_migrations.py
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chinook_project.settings')
django.setup()

def fix_migrations():
    print("Fixing migrations...")
    
    # Drop problematic table
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS chinook_app_userprofile;")
        print("✓ Dropped chinook_app_userprofile table")
    
    # Run migrate commands
    from django.core.management import call_command
    
    print("Running migrations...")
    call_command('migrate', '--fake-initial')
    
    print("Creating superuser...")
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✓ Superuser 'admin' created")
    else:
        print("✓ Superuser already exists")
    
    print("✅ Fix completed!")

if __name__ == "__main__":
    fix_migrations()