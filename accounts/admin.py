from django.contrib import admin
from django.contrib.auth.models import Group
from .models import UserProfile


# Custom admin for UserProfile with read-only role
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Show both fields in list view
    readonly_fields = ('role',)  # Make role read-only (cannot be edited)
    fields = ('user', 'role')  # Fields to display in edit form
    
    # Prevent adding UserProfiles manually (they're auto-created via signals)
    def has_add_permission(self, request):
        return False
    
    # Prevent deleting UserProfiles (tied to User model)
    def has_delete_permission(self, request, obj=None):
        return False


# Register UserProfile with custom admin
admin.site.unregister(UserProfile) if admin.site.is_registered(UserProfile) else None
admin.site.register(UserProfile, UserProfileAdmin)

# Hide Groups from admin sidebar (Groups are unused in this project)
# This is a UI-only change and does not affect authentication
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass  # Group was already unregistered, no action needed
