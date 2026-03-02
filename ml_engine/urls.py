from django.urls import path
from . import views

app_name = 'ml_engine'

urlpatterns = [
    path('predict/<int:application_id>/', views.predict_loan, name='predict_loan'),
]
