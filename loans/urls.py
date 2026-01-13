from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('apply/', views.apply_loan, name='apply_loan'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
