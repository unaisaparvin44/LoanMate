from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoanApplicationForm
from .models import LoanApplication

# Create your views here.

@login_required
def apply_loan(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'PENDING'
            application.save()
            messages.success(request, 'Your loan application has been submitted successfully! Our officers will review it soon.')
            return redirect("/user/dashboard/")
    else:
        form = LoanApplicationForm()
    
    return render(request, 'loans/apply_loan.html', {'form': form})

@login_required
def my_applications(request):
    applications = LoanApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'loans/my_applications.html', {'applications': applications})
