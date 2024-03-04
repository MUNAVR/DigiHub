from django.db import models
from app_1.models import Customers,Address1,Address2
from cart.models import Cart
# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(Customers,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    total_amount = models.DecimalField( max_digits=10, decimal_places=2)
    address=models.CharField(max_length=50,default='Unknown')
    order_date = models.DateTimeField(auto_now_add=True)





