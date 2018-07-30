from django.db import models

# Create your models here.

class Topping(models.Model):
    name = models.CharField(max_length=64)
    pass

class Extra(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    pass

class Menu_item(models.Model):
    category = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    sm_price = models.DecimalField(max_digits=5, decimal_places=2)
    lg_price = models.DecimalField(max_digits=5, decimal_places=2)
    toppings = models.ManyToManyField(Topping, blank=True)
    extras = models.ManyToManyField(Extra, blank=True)
