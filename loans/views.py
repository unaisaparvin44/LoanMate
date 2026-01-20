from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    LoanApplicationForm, 
    PersonalLoanForm, 
    HomeLoanForm, 
    EducationLoanForm, 
    VehicleLoanForm
)
from .models import LoanApplication, LoanType


@login_required
def apply_select_loan_type(request):
    """Display loan type selection page"""
    return render(request, 'loans/apply_select.html')


@login_required
def apply_personal_loan(request):
    """Handle Personal Loan application"""
    if request.method == 'POST':
        form = PersonalLoanForm(request.POST)
        if form.is_valid():
            try:
                # Get the loan type
                loan_type = LoanType.objects.get(name="Personal Loan", is_active=True)
                
                # Create the application
                application = LoanApplication(
                    user=request.user,
                    loan_type=loan_type,
                    loan_amount=form.cleaned_data['loan_amount'],
                    loan_tenure=form.cleaned_data['loan_tenure'],
                    income=form.cleaned_data['income'],
                    employment_type=form.cleaned_data['employment_type'],
                    credit_score=form.cleaned_data['credit_score'],
                    status='PENDING',
                    extra_details={
                        'purpose': form.cleaned_data['purpose'],
                        'existing_emi': form.cleaned_data['existing_emi'],
                        'emi_amount': form.cleaned_data.get('emi_amount', 0)
                    }
                )
                application.save()
                
                messages.success(request, 'Your Personal Loan application has been submitted successfully!')
                return redirect('loans:my_applications')
                
            except LoanType.DoesNotExist:
                messages.error(request, 'Personal Loan type is not available. Please contact support.')
                return render(request, 'loans/apply_personal.html', {'form': form})
    else:
        form = PersonalLoanForm()
    
    return render(request, 'loans/apply_personal.html', {'form': form})


@login_required
def apply_home_loan(request):
    """Handle Home Loan application"""
    if request.method == 'POST':
        form = HomeLoanForm(request.POST)
        if form.is_valid():
            try:
                # Get the loan type
                loan_type = LoanType.objects.get(name="Home Loan", is_active=True)
                
                # Create the application
                application = LoanApplication(
                    user=request.user,
                    loan_type=loan_type,
                    loan_amount=form.cleaned_data['loan_amount'],
                    loan_tenure=form.cleaned_data['loan_tenure'],
                    income=form.cleaned_data['income'],
                    employment_type=form.cleaned_data['employment_type'],
                    credit_score=form.cleaned_data['credit_score'],
                    status='PENDING',
                    extra_details={
                        'property_value': form.cleaned_data['property_value'],
                        'down_payment': form.cleaned_data['down_payment'],
                        'property_type': form.cleaned_data['property_type']
                    }
                )
                application.save()
                
                messages.success(request, 'Your Home Loan application has been submitted successfully!')
                return redirect('loans:my_applications')
                
            except LoanType.DoesNotExist:
                messages.error(request, 'Home Loan type is not available. Please contact support.')
                return render(request, 'loans/apply_home.html', {'form': form})
    else:
        form = HomeLoanForm()
    
    return render(request, 'loans/apply_home.html', {'form': form})


@login_required
def apply_education_loan(request):
    """Handle Education Loan application"""
    if request.method == 'POST':
        form = EducationLoanForm(request.POST)
        if form.is_valid():
            try:
                # Get the loan type
                loan_type = LoanType.objects.get(name="Education Loan", is_active=True)
                
                # Create the application
                application = LoanApplication(
                    user=request.user,
                    loan_type=loan_type,
                    loan_amount=form.cleaned_data['loan_amount'],
                    loan_tenure=form.cleaned_data['loan_tenure'],
                    income=form.cleaned_data['income'],
                    employment_type=form.cleaned_data['employment_type'],
                    credit_score=form.cleaned_data['credit_score'],
                    status='PENDING',
                    extra_details={
                        'course_name': form.cleaned_data['course_name'],
                        'university': form.cleaned_data['university'],
                        'course_duration_months': form.cleaned_data['course_duration_months']
                    }
                )
                application.save()
                
                messages.success(request, 'Your Education Loan application has been submitted successfully!')
                return redirect('loans:my_applications')
                
            except LoanType.DoesNotExist:
                messages.error(request, 'Education Loan type is not available. Please contact support.')
                return render(request, 'loans/apply_education.html', {'form': form})
    else:
        form = EducationLoanForm()
    
    return render(request, 'loans/apply_education.html', {'form': form})


@login_required
def apply_vehicle_loan(request):
    """Handle Vehicle Loan application"""
    if request.method == 'POST':
        form = VehicleLoanForm(request.POST)
        if form.is_valid():
            try:
                # Get the loan type
                loan_type = LoanType.objects.get(name="Vehicle Loan", is_active=True)
                
                # Create the application
                application = LoanApplication(
                    user=request.user,
                    loan_type=loan_type,
                    loan_amount=form.cleaned_data['loan_amount'],
                    loan_tenure=form.cleaned_data['loan_tenure'],
                    income=form.cleaned_data['income'],
                    employment_type=form.cleaned_data['employment_type'],
                    credit_score=form.cleaned_data['credit_score'],
                    status='PENDING',
                    extra_details={
                        'vehicle_type': form.cleaned_data['vehicle_type'],
                        'on_road_price': form.cleaned_data['on_road_price'],
                        'brand_model': form.cleaned_data.get('brand_model', '')
                    }
                )
                application.save()
                
                messages.success(request, 'Your Vehicle Loan application has been submitted successfully!')
                return redirect('loans:my_applications')
                
            except LoanType.DoesNotExist:
                messages.error(request, 'Vehicle Loan type is not available. Please contact support.')
                return render(request, 'loans/apply_vehicle.html', {'form': form})
    else:
        form = VehicleLoanForm()
    
    return render(request, 'loans/apply_vehicle.html', {'form': form})


# Keep old view for backward compatibility if needed
@login_required
def apply_loan(request):
    """Old apply loan view - now redirects to selection page"""
    return redirect('loans:apply_loan')


@login_required
def my_applications(request):
    applications = LoanApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'loans/my_applications.html', {'applications': applications})

