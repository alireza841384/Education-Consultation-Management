from django.db import models
from Accounts.models import CustomUser
from django.core.exceptions import ValidationError


class Report(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="reports")
    title=models.CharField(max_length=25)
    description=models.TextField(blank=True,max_length=250)
    uploaded_at=models.DateTimeField(auto_now_add=True)
    start_time=models.DateField()
    end_time=models.DateField()
    file = models.FileField(upload_to='reports/')
    class Meta:
        ordering = ["-uploaded_at"]
    def clean(self):
            errors={}

            if self.user_id and self.user.type!=CustomUser.Types.STUDENT:
                errors["user"]="Only users with student type can send reports."

            if self.start_time and self.end_time and self.start_time>=self.end_time:
                errors["end_time"]="End date must be after start date."

            if errors:
                raise ValidationError(errors)

            return super().clean()


    def __str__(self):
        date_str = self.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if self.uploaded_at else "Unsaved"
        return f"report-{self.user.email}-{date_str}"



    