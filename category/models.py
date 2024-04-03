from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=15,db_index=True,unique=True)
    is_active = models.BooleanField(default=True)
    sale_count=models.CharField(max_length=10,default=0)
    

    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Brand(models.Model):
    name=models.CharField(max_length=15)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    offer=models.DecimalField(max_digits=5, decimal_places=2,null=True)
    sale_count=models.CharField(max_length=15,default=0)

