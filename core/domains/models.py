from django.db import models
from django.contrib.auth.models import User
import uuid

class Website(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # 👈 ADD THIS
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    widget_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class WebsiteSnapshot(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="snapshots"
    )
    html = models.TextField()   # ← this field MUST exist
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Snapshot - {self.website.domain}"
