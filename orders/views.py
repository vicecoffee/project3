from django.http import HttpResponse
from django.shortcuts import render
from orders.models import Menu_item

# Create your views here.
def index(request):
    return render(request, "index.html")

def menu(request):
    menu_items = Menu_item.objects.all()
    return render(request, "menu.html",{"menu_items": menu_items})
