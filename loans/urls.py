from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('apply/', views.apply_select_loan_type, name='apply_loan'),
    path('apply/personal/', views.apply_personal_loan, name='apply_personal_loan'),
    path('apply/home/', views.apply_home_loan, name='apply_home_loan'),
    path('apply/education/', views.apply_education_loan, name='apply_education_loan'),
    path('apply/vehicle/', views.apply_vehicle_loan, name='apply_vehicle_loan'),
    path('my-applications/', views.my_applications, name='my_applications'),
]

