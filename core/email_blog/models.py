from django.db import models   # ✅ THIS LINE WAS MISSING
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBlog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
