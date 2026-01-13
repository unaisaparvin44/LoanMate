from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('redirect/', views.role_redirect, name='role_redirect'),
]
