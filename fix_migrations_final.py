# fix_migrations_final.py
import os
import sys
import django
from django.db import connection
from django.db.models.signals import post_save

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chinook_project.settings')
django.setup()

def fix_migrations():
    print("Fixing migrations...")
    
    # Temporarily disconnect the signal
    from chinook_app.models import create_user_profile
    from django.contrib.auth.models import User
    
    print("Disconnecting post_save signal...")
    post_save.disconnect(create_user_profile, sender=User)
    
    # Run migrations
    from django.core.management import call_command
    
    print("Running migrations...")
    call_command('migrate')
    
    print("Creating superuser...")
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✓ Superuser 'admin' created")
    else:
        print("✓ Superuser already exists")
    
    # Reconnect the signal
    print("Reconnecting post_save signal...")
    from chinook_app.models import create_user_profile
    post_save.connect(create_user_profile, sender=User)
    
    print("✅ Fix completed!")

if __name__ == "__main__":
    fix_migrations()