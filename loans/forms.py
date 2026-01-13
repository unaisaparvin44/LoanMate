from django import forms
from .models import LoanApplication, LoanType

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_type', 'income', 'employment_type', 'credit_score', 'loan_amount', 'loan_tenure']
        # Exclude: user, status, created_at

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # loan_type queryset must be active LoanTypes
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
