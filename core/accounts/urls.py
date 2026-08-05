from django.urls import path
from .views import register, login_view
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetConfirmView

from .forms import CustomPasswordResetForm   # 👈 ADD THIS IMPORT

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
   path("password-reset/",
         auth_views.PasswordResetView.as_view(
             template_name="accounts/password_reset.html",
             form_class=CustomPasswordResetForm
         ),
         name="password_reset"),

    path("password-reset/done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="accounts/password_reset_done.html"
         ),
         name="password_reset_done"),

    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm"
    ),

    path("reset/done/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="accounts/password_reset_complete.html"
         ),
         name="password_reset_complete"),
]