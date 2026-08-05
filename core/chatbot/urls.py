from django.urls import path
from . import views  
from .views import embed

urlpatterns = [
    path("", views.chat, name="chat"),              # normal page (optional)
    path("embed/", views.embed, name="embed"),      # iframe container
    path("widget/", views.chat_widget, name="widget"),  # ✅ REAL CHAT UI
    path("api/", views.chat_api, name="chat_api"),  # AI API
]
