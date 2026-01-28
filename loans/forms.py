from django import forms
from .models import LoanApplication, LoanType


class BaseLoanApplicationForm(forms.Form):
    """Base form with common fields for all loan types"""
    loan_amount = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter loan amount'})
    )
    loan_tenure = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter tenure in months'}),
        help_text="Loan tenure in months"
    )
    income = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter monthly income'})
    )
    employment_type = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Full-time, Part-time, Self-employed'})
    )
    credit_score = forms.IntegerField(
        min_value=300,
        max_value=900,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter credit score (300-900)'})
    )

    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Loan amount must be greater than zero.")
        return amount

    def clean_loan_tenure(self):
        tenure = self.cleaned_data.get('loan_tenure')
        if tenure is not None and tenure <= 0:
            raise forms.ValidationError("Loan tenure must be greater than zero.")
        return tenure

    def clean_credit_score(self):
        score = self.cleaned_data.get('credit_score')
        if score is not None:
            if score < 300 or score > 900:
                raise forms.ValidationError("Credit score must be between 300 and 900.")
        return score


class PersonalLoanForm(BaseLoanApplicationForm):
    """Form for Personal Loan with specific fields"""
    purpose = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Wedding, Medical, Education'}),
        help_text="Purpose of the loan"
    )
    existing_emi = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Do you have existing EMIs?"
    )
    emi_amount = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter current EMI amount'}),
        help_text="Current monthly EMI amount (if applicable)"
    )

    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        MIN_LOAN_AMOUNT = 10000  # ₹10,000
        MAX_PERSONAL_LOAN = 500000  # ₹5,00,000
        
        if amount is not None:
            if amount <= 0:
                raise forms.ValidationError("Loan amount must be greater than zero.")
            if amount < MIN_LOAN_AMOUNT:
                raise forms.ValidationError(
                    f"Personal loan amount must be at least ₹10,000. You requested ₹{amount:,}."
                )
            if amount > MAX_PERSONAL_LOAN:
                raise forms.ValidationError(
                    f"Personal loan amount cannot exceed ₹5,00,000. You requested ₹{amount:,}. "
                    f"Please reduce your loan amount by ₹{amount - MAX_PERSONAL_LOAN:,}."
                )
        return amount

    def clean(self):
        cleaned_data = super().clean()
        existing_emi = cleaned_data.get('existing_emi')
        emi_amount = cleaned_data.get('emi_amount')

        if existing_emi and not emi_amount:
            raise forms.ValidationError("Please provide EMI amount if you have existing EMIs.")
        
        return cleaned_data


class HomeLoanForm(BaseLoanApplicationForm):
    """Form for Home Loan with specific fields"""
    PROPERTY_TYPE_CHOICES = [
        ('Apartment', 'Apartment'),
        ('House', 'House'),
        ('Villa', 'Villa'),
        ('Plot', 'Plot'),
    ]

    property_value = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total property value'}),
        help_text="Total value of the property"
    )
    down_payment = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter down payment amount'}),
        help_text="Down payment amount"
    )
    property_type = forms.ChoiceField(
        choices=PROPERTY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        MIN_LOAN_AMOUNT = 10000  # ₹10,000
        MAX_HOME_LOAN = 10000000  # ₹1,00,00,000 (1 Crore)
        
        if amount is not None:
            if amount <= 0:
                raise forms.ValidationError("Loan amount must be greater than zero.")
            if amount < MIN_LOAN_AMOUNT:
                raise forms.ValidationError(
                    f"Home loan amount must be at least ₹10,000. You requested ₹{amount:,}."
                )
            if amount > MAX_HOME_LOAN:
                raise forms.ValidationError(
                    f"Home loan amount cannot exceed ₹1,00,00,000. You requested ₹{amount:,}. "
                    f"Please reduce your loan amount by ₹{amount - MAX_HOME_LOAN:,}."
                )
        return amount

    def clean(self):
        cleaned_data = super().clean()
        property_value = cleaned_data.get('property_value')
        down_payment = cleaned_data.get('down_payment')

        if property_value and down_payment:
            if down_payment >= property_value:
                raise forms.ValidationError("Down payment must be less than property value.")
        
        return cleaned_data


class EducationLoanForm(BaseLoanApplicationForm):
    """Form for Education Loan with specific fields"""
    course_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Master of Computer Science'}),
        help_text="Name of the course"
    )
    university = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Stanford University'}),
        help_text="University or institution name"
    )
    course_duration_months = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter course duration in months'}),
        help_text="Course duration in months"
    )

    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        MIN_LOAN_AMOUNT = 10000  # ₹10,000
        MAX_EDUCATION_LOAN = 2000000  # ₹20,00,000 (20 Lakhs)
        
        if amount is not None:
            if amount <= 0:
                raise forms.ValidationError("Loan amount must be greater than zero.")
            if amount < MIN_LOAN_AMOUNT:
                raise forms.ValidationError(
                    f"Education loan amount must be at least ₹10,000. You requested ₹{amount:,}."
                )
            if amount > MAX_EDUCATION_LOAN:
                raise forms.ValidationError(
                    f"Education loan amount cannot exceed ₹20,00,000. You requested ₹{amount:,}. "
                    f"Please reduce your loan amount by ₹{amount - MAX_EDUCATION_LOAN:,}."
                )
        return amount


class VehicleLoanForm(BaseLoanApplicationForm):
    """Form for Vehicle Loan with specific fields"""
    VEHICLE_TYPE_CHOICES = [
        ('Car', 'Car'),
        ('Bike', 'Bike'),
        ('Commercial', 'Commercial Vehicle'),
    ]

    vehicle_type = forms.ChoiceField(
        choices=VEHICLE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    on_road_price = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter vehicle on-road price'}),
        help_text="Vehicle on-road price"
    )
    brand_model = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Honda City, Royal Enfield Classic'}),
        help_text="Vehicle brand and model (optional)"
    )

    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        MIN_LOAN_AMOUNT = 10000  # ₹10,000
        MAX_VEHICLE_LOAN = 1500000  # ₹15,00,000 (15 Lakhs)
        
        if amount is not None:
            if amount <= 0:
                raise forms.ValidationError("Loan amount must be greater than zero.")
            if amount < MIN_LOAN_AMOUNT:
                raise forms.ValidationError(
                    f"Vehicle loan amount must be at least ₹10,000. You requested ₹{amount:,}."
                )
            if amount > MAX_VEHICLE_LOAN:
                raise forms.ValidationError(
                    f"Vehicle loan amount cannot exceed ₹15,00,000. You requested ₹{amount:,}. "
                    f"Please reduce your loan amount by ₹{amount - MAX_VEHICLE_LOAN:,}."
                )
        return amount


# Keep the old form for backward compatibility if needed
class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_type', 'income', 'employment_type', 'credit_score', 'loan_amount', 'loan_tenure']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_type'].queryset = LoanType.objects.filter(is_active=True)

    def clean_loan_amount(self):
        amount = self.cleaned_data.get('loan_amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Loan amount must be greater than zero.")
        return amount

    def clean_loan_tenure(self):
        tenure = self.cleaned_data.get('loan_tenure')
        if tenure is not None and tenure <= 0:
            raise forms.ValidationError("Loan tenure must be greater than zero.")
        return tenure

    def clean_credit_score(self):
        score = self.cleaned_data.get('credit_score')
        if score is not None:
            if score < 300 or score > 900:
                raise forms.ValidationError("Credit score must be between 300 and 900.")
        return score

