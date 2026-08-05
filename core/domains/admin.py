from django.contrib import admin
from .models import Website

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "widget_id", "created_at")
    readonly_fields = ("widget_id",)
