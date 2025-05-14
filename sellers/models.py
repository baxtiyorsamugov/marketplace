from django.db import models
from django.conf import settings

class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='seller_logos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name
