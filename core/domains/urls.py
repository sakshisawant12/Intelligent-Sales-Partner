from django.urls import path
from . import views

app_name = "domains"

urlpatterns = [
    path("", views.registered_websites, name="registered_websites"),
    path("add/", views.add_website, name="add_website"),
    path("<uuid:website_id>/", views.website_code, name="website_code"),
]
