from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.contrib import messages
import re
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from email_blog.views import send_email_manual   # ✅ using manual email


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Confirm password
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        # Password rules
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect("register")

        if not re.search(r"[A-Z]", password1):
            messages.error(request, "Password must contain 1 uppercase letter")
            return redirect("register")

        if not re.search(r"[a-z]", password1):
            messages.error(request, "Password must contain 1 lowercase letter")
            return redirect("register")

        if not re.search(r"[0-9]", password1):
            messages.error(request, "Password must contain 1 number")
            return redirect("register")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            messages.error(request, "Password must contain 1 special character")
            return redirect("register")

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1
        )

        # ✅ OWNER NOTIFICATION MAIL
        send_email_manual(
            "New User Registered on ISP",
            f"New user registered with email: {email}",
            settings.ISP_OWNER_EMAIL
        )

        # ✅ USER WELCOME MAIL
        send_email_manual(
            "Welcome to Intelligent Sales Partner 🎉",
            (
                "Hi 👋\n\n"
                "Welcome to Intelligent Sales Partner!\n\n"
                "Your account has been created successfully.\n"
                "You can now log in and start using your AI chatbot.\n\n"
                "If you have any questions, just reply to this email.\n\n"
                "– Team ISP"
            ),
            email
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return redirect("/dashboard/")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "accounts/login.html")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

    def form_valid(self, form):
        user = form.save()

        # ✅ PASSWORD CHANGED EMAIL (manual SMTP)
        send_email_manual(
            "Your password has been changed",
            (
                "Hi 👋\n\n"
                "Your password was changed successfully.\n\n"
                "If this was not you, please reset your password immediately.\n\n"
                "– Intelligent Sales Partner Team"
            ),
            user.email
        )

        return super().form_valid(form)