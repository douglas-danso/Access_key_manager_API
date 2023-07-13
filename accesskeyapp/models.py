from django.db import models
from tryapp.models import CustomUser

class AccessKey(models.Model):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    REVOKED = 'revoked'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (REVOKED, 'Revoked'),
    ]
    
    key = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=ACTIVE)
    date_of_procurement = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    school = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
