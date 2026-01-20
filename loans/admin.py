from django.contrib import admin
from .models import LoanType, LoanApplication


class LoanApplicationAdmin(admin.ModelAdmin):
    """
    Custom admin for LoanApplication that disables manual creation.
    Loan applications should only be created by end-users through the application form.
    """
    # Display configuration for better admin UX
    list_display = ['user', 'loan_type', 'loan_amount', 'loan_tenure', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'loan_type', 'created_at', 'reviewed_at']
    search_fields = ['user__username', 'user__email', 'remarks']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    # Disable the ability to add new loan applications from admin
    def has_add_permission(self, request):
        """
        Remove the 'Add' button and prevent manual creation of loan applications.
        Applications must come from end-users only.
        """
        return False


admin.site.register(LoanType)
admin.site.register(LoanApplication, LoanApplicationAdmin)
