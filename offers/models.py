from django.db import models
from app_1.models import Customers
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import datetime
# Assuming Customers is your custom user model

class ReferralOffer(models.Model):
    offer_code = models.CharField(max_length=10, unique=True, editable=False)
    referral_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount to credit to the user's wallet
    valid_from = models.DateField(auto_now_add=True)
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)

    referral_code = models.CharField(max_length=10, unique=True, editable=False)  # Auto-generated referral code
    referred_by = models.ForeignKey(Customers, related_name='referrals', on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        if not self.offer_code:
            self.offer_code = get_random_string(length=10)
        if not self.referral_code:
            self.referral_code = get_random_string(length=10)
        super().save(*args, **kwargs)  # Call the save method of the parent class

    def __str__(self):
        return self.offer_code

