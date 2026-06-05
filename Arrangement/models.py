from django.db import models
from Accounts.models import CustomUser

# Create your models here.


class ArrangementFile(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="plans")
    admin=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="plans_uploaded")
    title=models.CharField(max_length=25)
    description=models.TextField(blank=True,max_length=250)
    uploaded_at=models.DateField(auto_now_add=True)
    start_time=models.DateField()
    end_time=models.DateField()
    file = models.FileField(upload_to='arrangements/')
    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        date_str = self.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if self.uploaded_at else "Unsaved"
        return f"plan-{self.user.email}-{date_str}"