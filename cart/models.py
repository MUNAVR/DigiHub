from django.db import models
from app_1.models import Customers
from products.models import Product_Variant

# Create your models here.
class Cart(models.Model):
    user_id=models.ForeignKey(Customers,on_delete=models.CASCADE)
    product_variant=models.ForeignKey(Product_Variant,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class CartItems(models.Model):
    user_id=models.ForeignKey(Customers,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)