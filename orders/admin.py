from django.contrib import admin

# Register your models here.
from .models import Menu_item, Topping, Extra

admin.site.register(Menu_item)
admin.site.register(Topping)
admin.site.register(Extra)