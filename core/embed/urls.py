from django.urls import path
from .views import embed_js

urlpatterns = [
    path("<uuid:website_id>.js", embed_js),
]
