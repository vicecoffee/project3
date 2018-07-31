from django.contrib import admin

# Register your models here.
from .models import Menu_item, Topping, Extra, Order, Order_item, Cart, Cart_item

# So that items can be edited from the order or cart in the UI
# From https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#inlinemodeladmin-objects
class OrderItemInline(admin.TabularInline):
    model = Order_item

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]

class CartItemInline(admin.TabularInline):
    model = Cart_item

class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartItemInline,
    ]

admin.site.register(Menu_item)
admin.site.register(Topping)
admin.site.register(Extra)
admin.site.register(Order, OrderAdmin)
admin.site.register(Order_item)
admin.site.register(Cart, CartAdmin)
admin.site.register(Cart_item)
