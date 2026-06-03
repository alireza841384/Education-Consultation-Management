from django.db import models
from django.conf import settings


class Report(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    content = models.TextField(blank=True)
    picture = models.ImageField(upload_to="report_pictures/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "Unsaved"
        return f"Report-{self.user.email}-{date_str}"
