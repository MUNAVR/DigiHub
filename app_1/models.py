from django.db import models

# Create your models here.

class Customers(models.Model):
    first_name=models.CharField(max_length=20,blank=True)
    last_name = models.CharField(max_length=25,blank=True)
    email = models.EmailField(unique=True)
    phone = models.BigIntegerField(blank=True)
    password=models.CharField(max_length=30,blank=True,unique=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name

class Address1(models.Model):
    user = models.ForeignKey(Customers,on_delete=models.CASCADE)
    address = models.CharField(max_length=30)
    locality = models.CharField(max_length=20)
    pincode = models.IntegerField()
    district = models.CharField(max_length=14)
    state = models.CharField(max_length=10)

class Address2(models.Model):
    user = models.ForeignKey(Customers, on_delete=models.CASCADE)
    address = models.CharField(max_length=30)
    locality = models.CharField(max_length=20)
    pincode = models.IntegerField()
    district = models.CharField(max_length=14)
    state = models.CharField(max_length=10)


