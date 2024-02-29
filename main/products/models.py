from django.db import models
from category.models import Brand
from category.models import Category
import re
from django.utils.text import slugify

# Create your models here.


# Atribute Value - ( RED,BLUE, 4GB, 8GB, 128GB )---------------------------------------
    
class Attribute_Value(models.Model):
    attribute_color = models.CharField(max_length = 50)
    attribute_ram = models.CharField(max_length = 50)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.attribute_color
    
# Products----------------------------------------------------------------------------------------

class Products(models.Model):
    product_name=models.CharField(max_length=100)
    product_category=models.ForeignKey(Category,on_delete=models.CASCADE)
    product_brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now_add=True)
    product_description = models.TextField(max_length=250)


    def __str__(self):
        return self.product_brand.name+"-"+self.product_name

    

# Variant-----------------------------------------------------------------------------------------
class Product_Variant(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    attributes = models.ManyToManyField(Attribute_Value,related_name='attributes')
    max_price = models.DecimalField(max_digits=7, decimal_places=3)
    sale_price = models.DecimalField(max_digits=7, decimal_places=3)
    stock = models.IntegerField()
    thumbnail_image = models.ImageField(upload_to='images/')
    is_active = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.product_variant.product

    
