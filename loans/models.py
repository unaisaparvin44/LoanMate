from django.db import models
from django.conf import settings


class LoanType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LoanApplication(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    loan_type = models.ForeignKey(
        LoanType,
        on_delete=models.PROTECT
    )
    income = models.PositiveIntegerField()
    employment_type = models.CharField(max_length=50)
    credit_score = models.PositiveIntegerField()
    loan_amount = models.PositiveIntegerField()
    loan_tenure = models.PositiveIntegerField(
        help_text="Loan tenure in months"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.loan_type} - {self.status}"
