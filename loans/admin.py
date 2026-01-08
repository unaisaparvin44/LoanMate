from django.contrib import admin
from .models import LoanType, LoanApplication

admin.site.register(LoanType)
admin.site.register(LoanApplication)
