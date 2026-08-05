from django.urls import path
from . import views
from email_blog.views import email_marketing

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("test/", views.test_page, name="test"),
    path("domains/", views.domains, name="dashboard_domains"),
    path("conversations/", views.conversations, name="dashboard_conversations"),
    path("settings/", views.settings_view, name="dashboard_settings"),

    path(
    "email-marketing/",
    email_marketing,
    name="dashboard_email_marketing"
    ),
    path("leads/", views.leads, name="dashboard_leads"),
    path("change-theme/", views.change_theme, name="change_theme"),
    path("toggle-theme/", views.toggle_theme, name="toggle_theme"),
    path(
    "conversations/<int:conversation_id>/",
    views.conversation_detail,
    name="conversation_detail"
    ),
    path(
    "website/<int:website_id>/",
    views.website_dashboard,
    name="website_dashboard"
    ),
    path(
    "website/<int:website_id>/leads/",
    views.website_leads,
    name="website_leads"
    ),
    path(
    "set-website/<int:website_id>/",
    views.set_current_website,
    name="set_current_website"
    ),
    path("settings/update-email/", views.update_email, name="update_email"),
    path("settings/delete-account/", views.delete_account, name="delete_account"),


]
