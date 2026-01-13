import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loanmate.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Target credentials
target_username = 'admin'
new_password = 'LoanMateAdmin@123'

try:
    user = User.objects.get(username=target_username)
    user.set_password(new_password)
    user.save()
    print(f"SUCCESS: Password updated for user '{target_username}'.")
except User.DoesNotExist:
    print(f"User '{target_username}' not found. Creating new superuser.")
    User.objects.create_superuser(target_username, 'admin@example.com', new_password)
    print(f"SUCCESS: Created new superuser '{target_username}'.")
except Exception as e:
    print(f"ERROR: {e}")
