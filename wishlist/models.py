from django.db import models
from django.db import models
from app_1.models import Customers
from products.models import Product_Variant

class Wishlist(models.Model):
    user = models.OneToOneField(Customers, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product_Variant)

    def add_to_wishlist(self, product):
        self.products.add(product)

    def remove_from_wishlist(self, product):
        self.products.remove(product)

    def clear_wishlist(self):
        self.products.clear()
