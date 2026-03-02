import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from loans.models import LoanApplication


@login_required
def admin_reports(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied. Staff privileges required.")

    applications = LoanApplication.objects.select_related('user', 'loan_type', 'reviewed_by').all()

    context = {
        'total': applications.count(),
        'approved': applications.filter(status='APPROVED').count(),
        'rejected': applications.filter(status='REJECTED').count(),
        'pending': applications.filter(status='PENDING').count(),
        'applications': applications,
    }
    return render(request, 'reports/admin_reports.html', context)


@login_required
def export_admin_csv(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied. Staff privileges required.")

    applications = LoanApplication.objects.select_related('user', 'loan_type', 'reviewed_by').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_report.csv"'
    writer = csv.writer(response)

    writer.writerow(['ID', 'User', 'Loan Type', 'Amount', 'Status', 'Created At', 'Reviewed At', 'Reviewed By'])

    for app in applications:
        writer.writerow([
            app.id,
            app.user.username,
            app.loan_type.name,
            app.loan_amount,           # correct field name from model
            app.status,
            app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else '',
            app.reviewed_at.strftime('%Y-%m-%d %H:%M') if app.reviewed_at else '',
            app.reviewed_by.username if app.reviewed_by else 'N/A',
        ])

    return response


@login_required
def officer_reports(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'officer':
        return HttpResponseForbidden("Access denied. Officer role required.")

    applications = LoanApplication.objects.select_related(
        'user', 'loan_type'
    ).filter(reviewed_by=request.user)

    context = {
        'total': applications.count(),
        'approved': applications.filter(status='APPROVED').count(),
        'rejected': applications.filter(status='REJECTED').count(),
        'applications': applications,
    }
    return render(request, 'reports/officer_reports.html', context)


@login_required
def export_officer_csv(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'officer':
        return HttpResponseForbidden("Access denied. Officer role required.")

    applications = LoanApplication.objects.select_related(
        'user', 'loan_type'
    ).filter(reviewed_by=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="officer_report.csv"'
    writer = csv.writer(response)

    writer.writerow(['ID', 'User', 'Loan Type', 'Amount', 'Status', 'Created At', 'Reviewed At'])

    for app in applications:
        writer.writerow([
            app.id,
            app.user.username,
            app.loan_type.name,
            app.loan_amount,           # correct field name from model
            app.status,
            app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else '',
            app.reviewed_at.strftime('%Y-%m-%d %H:%M') if app.reviewed_at else '',
        ])

    return response
