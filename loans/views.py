from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoanApplicationForm
from .models import LoanApplication

# Create your views here.

@login_required
def apply_loan(request):
    success = False
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'PENDING'
            application.save()
            success = True
            form = LoanApplicationForm()  # Reset form after successful submission
    else:
        form = LoanApplicationForm()
    
    return render(request, 'loans/apply_loan.html', {'form': form, 'success': success})

@login_required
def my_applications(request):
    applications = LoanApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'loans/my_applications.html', {'applications': applications})
