"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chatbot.urls")),
    path(
    "dashboard/",
    include(("dashboard.urls", "dashboard"), namespace="dashboard")
    ),

    path("domains/", include("domains.urls")), 
    path("embed/", include("embed.urls")),
    path("contact/", lambda request: render(request, "website/contact.html")),
    path("features/", lambda request: render(request, "website/features.html")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0]
    )
