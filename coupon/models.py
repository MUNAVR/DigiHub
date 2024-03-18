from django.db import models
from django.utils import timezone
from app_1.models import Customers

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    max_usage = models.PositiveIntegerField(default=1)
    usage_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def is_valid(self):
        """
        Method to check if the coupon is still valid based on its valid_from, valid_to, and active status.
        """
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and self.usage_count < self.max_usage

    def increment_usage(self):
        """
        Method to increment the usage count of the coupon.
        """
        self.usage_count += 1
        self.save()

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    user = models.ForeignKey(Customers, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    date_used = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coupon')