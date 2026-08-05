from django.db import models
from domains.models import Website

class Lead(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="leads",
    )

    email = models.EmailField()
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    source = models.CharField(
        max_length=20,
        choices=(
            ("chatbot", "Chatbot"),
            ("contact_form", "Contact Form"),
        ),
        blank=True,
        null=True,
    )

    intent = models.CharField(
        max_length=20,
        choices=(
            ("pricing", "Pricing"),
            ("interest", "Interest"),
            ("contact", "Contact"),
            ("general", "General"),
        ),
        default="general",
    )

    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("website", "email")

    def __str__(self):
        return f"{self.email} ({self.website.domain})"
