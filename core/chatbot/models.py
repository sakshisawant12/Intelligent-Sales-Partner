from django.db import models
from domains.models import Website

class Chatbot(models.Model):
    name = models.CharField(max_length=100)
    welcome_message = models.TextField()

    def __str__(self):
        return self.name
    
class Conversation(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="conversations"
    )
    email = models.EmailField()
    human_requested = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "email")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.email} - {self.website.domain}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.CharField(
        max_length=10,
        choices=[
            ("user", "User"),
            ("bot", "Bot"),
            ("human", "Human Agent"),
        ]
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.text[:40]}"