from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your models here.

class Topping(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Extra(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Menu_item(models.Model):
    category = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    sm_price = models.DecimalField(max_digits=5, decimal_places=2)
    lg_price = models.DecimalField(max_digits=5, decimal_places=2)
    toppings = models.ManyToManyField(Topping, blank=True)
    extras = models.ManyToManyField(Extra, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.category)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    @property
    def total(self):
        total_amt = 0
        for line in self.order_item_set.all():
            total_amt += line.total

        return total_amt

    @property
    def total_quantity(self):
        return self.order_item_set.aggregate(total_quantity = Sum("quantity"))["total_quantity"]

    def __str__(self):
        return "{} ({})".format(self.id, self.user.username)

class Order_item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu_item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_large = models.BooleanField(default=False)

    @property
    def description(self):
        size_text = ""
        if self.item.sm_price != self.item.lg_price:
            size_text = "Large" if self.is_large else "Small"

        return "{} {} {} ({})".format(size_text, self.item.name, self.item.category, self.quantity)

    @property
    def unit_price(self):
        return self.item.lg_price if self.is_large else self.item.sm_price

    @property
    def total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return "{} (order id: {})".format(self.description, self.order.id)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def total(self):
        total_amt = 0
        for line in self.cart_item_set.all():
            total_amt += line.total

        return total_amt

    @property
    def total_quantity(self):
        return self.cart_item_set.aggregate(total_quantity = Sum("quantity"))["total_quantity"]

    def __str__(self):
        return "{} ({})".format(self.id, self.user.username)

class Cart_item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu_item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_large = models.BooleanField(default=False)

    @property
    def description(self):
        size_text = ""
        if self.item.sm_price != self.item.lg_price:
            size_text = "Large" if self.is_large else "Small"

        return "{} {} {} ({})".format(size_text, self.item.name, self.item.category, self.quantity)

    @property
    def unit_price(self):
        return self.item.lg_price if self.is_large else self.item.sm_price

    @property
    def total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return "{} (cart id: {})".format(self.description, self.cart.id)


# Could not think of a good way to have both Cart and Order classes share the common code for properties