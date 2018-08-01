from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your models here.

class Topping(models.Model):
    name = models.CharField(max_length=64)

    # Adding a __str__ method so that automated things like Django db admin screens have readable names
    def __str__(self):
        return self.name

class Extra(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return "{} - ${}".format(self.name, self.price)

class Menu_item(models.Model):
    category = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    sm_price = models.DecimalField(max_digits=5, decimal_places=2)
    lg_price = models.DecimalField(max_digits=5, decimal_places=2)
    toppings = models.ManyToManyField(Topping, blank=True)
    extras = models.ManyToManyField(Extra, blank=True)

    # Property tag means I can use .has_sizes instead of .has_sizes()
    @property
    def has_sizes(self):
        return self.sm_price != self.lg_price

    def __str__(self):
        return "{} ({})".format(self.name, self.category)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # From https://docs.djangoproject.com/en/2.0/ref/models/fields/
    SHOPPING = 'SH'
    PLACED = 'PL'
    COMPLETED = 'CO'
    STATUS_CHOICES = (
        (SHOPPING, 'Still Shopping'),
        (PLACED, 'Placed'),
        (COMPLETED, 'Complete')
    )

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=SHOPPING
    )

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
    SMALL = 'SM'
    LARGE = 'LG'
    NA = 'NA'
    SIZE_CHOICES = (
        (SMALL, 'Small'),
        (LARGE, 'Large'),
        (NA, 'Not Applicable')
    )

    size = models.CharField(
        max_length=2,
        choices=SIZE_CHOICES,
        default=NA
    )

    toppings = models.ManyToManyField(Topping, blank=True)
    extras = models.ManyToManyField(Extra, blank=True)

    @property
    def description(self):
        # Change the tuple into a dict to get the longer name for the size
        return "{} {} {} ({})".format(
            dict(self.SIZE_CHOICES)[self.size] if self.size != self.NA else "",
            self.item.name,
            self.item.category,
            self.quantity
            )

    @property
    def unit_price(self):
        return self.item.lg_price if self.size == self.LARGE else self.item.sm_price

    @property
    def total(self):
        extra_price = self.extras.aggregate(total = Sum('price'))['total']
        return (self.unit_price + (extra_price if extra_price is not None else 0)) * self.quantity

    def __str__(self):
        return "{} (order id: {})".format(self.description, self.order.id)