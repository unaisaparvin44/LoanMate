from django.urls import path
from . import views

app_name = 'officers'

urlpatterns = [
    path('profile/', views.officer_profile, name='officer_profile'),
    path('applications/', views.officer_application_list, name='application_list'),
    path('applications/all/', views.officer_application_all, name='application_all'),
    path('applications/<int:pk>/', views.officer_application_detail, name='application_detail'),
]
