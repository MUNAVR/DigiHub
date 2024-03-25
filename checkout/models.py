from django.db import models
from app_1.models import Customers,Address1,Address2
from cart.models import Cart
# Create your models here.

class Checkout(models.Model):
    user = models.ForeignKey(Customers, on_delete=models.CASCADE)
    cart_items=models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    subtotal=models.DecimalField(max_digits=10, decimal_places=2)

class Order(models.Model):
    user = models.ForeignKey(Customers, on_delete=models.CASCADE)
    subtotal=models.DecimalField(max_digits=10, decimal_places=2,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=15, default="Pending")
    payment_method = models.CharField(max_length=15, default="COD")
    order_status = models.CharField(max_length=15, default="Pending")
    delivery_date = models.DateTimeField(null=True, blank=True)
    coupon=models.CharField(max_length=15, default="No Coupon")

class OrderAddress(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(Customers,on_delete=models.CASCADE)
    address = models.CharField(max_length=30)
    locality = models.CharField(max_length=20)
    pincode = models.IntegerField()
    district = models.CharField(max_length=14)
    state = models.CharField(max_length=10)
    

class OrderProduct(models.Model):
    user = models.ForeignKey(Customers,on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    