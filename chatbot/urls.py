from django.urls import path
from chatbot import views

app_name = "chatbot"

urlpatterns = [
    path("faq/", views.chatbot_response, name="chatbot_faq"),
]
