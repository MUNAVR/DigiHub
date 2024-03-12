from django.db import models
from app_1.models import Customers


class Wallet(models.Model):
    user = models.OneToOneField(Customers, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)

   