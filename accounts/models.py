from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('officer', 'Officer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    # Profile fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    employment_type = models.CharField(max_length=50, blank=True, null=True)
    monthly_income = models.PositiveIntegerField(blank=True, null=True)

    # Officer-specific fields
    designation = models.CharField(max_length=100, blank=True, null=True)
    experience = models.PositiveIntegerField(blank=True, null=True, help_text="Years of experience")
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
