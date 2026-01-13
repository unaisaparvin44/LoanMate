from django.contrib import admin
from django.contrib.auth.models import Group
from .models import UserProfile

# Register UserProfile in admin
admin.site.register(UserProfile)

# Hide Groups from admin sidebar (Groups are unused in this project)
# This is a UI-only change and does not affect authentication
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass  # Group was already unregistered, no action needed
