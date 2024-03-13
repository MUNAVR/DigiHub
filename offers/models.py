from django.db import models
from app_1.models import Customers
from products.models import Products, Product_Variant
from category.models import Brand
from django.utils.crypto import get_random_string
from django.utils import timezone
# Create your models here.



class BaseOffer(models.Model):
    class Meta:
        abstract = True

    offer_code = models.CharField(max_length=10, unique=True, editable=False)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_discountAmount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_discountAmount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField(auto_now_add=True)
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)  # New field added

    def save(self, *args, **kwargs):
        if not self.offer_code:
            self.offer_code = get_random_string(length=10)
        # Check if the offer has expired before saving
        if self.valid_to < timezone.now().date():
            self.delete()  # Delete the offer if it has expired
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.offer_code


class ReferralOffer(BaseOffer):
    class Meta:
        db_table = "Referral_Offer"
        managed = True

    referral_code = models.CharField(max_length=10, unique=True)
    referred_by = models.ForeignKey(Customers, related_name='referrals', on_delete=models.SET_NULL, null=True)


class ProductOffer(BaseOffer):
    class Meta:
        db_table = "Product_Offer"
        managed = True

    product = models.ForeignKey(Products, on_delete=models.CASCADE)


class BrandOffer(BaseOffer):
    class Meta:
        db_table = "Brand_Offer"
        managed = True

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

