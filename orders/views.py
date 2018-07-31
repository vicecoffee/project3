from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from orders.models import Menu_item, Order, Cart, Order_item
from .forms import RegisterForm
from django import forms
from json import dumps

# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required
def menu(request):
    if request.method == "POST":
        item_id = 5
        is_large = False
        quantity = 3

        item = Menu_item.objects.get(id = item_id)

        if item is None:
            return HttpResponse("invalid item")

        cart, created = Cart.objects.get_or_create(user = request.user)

        line = cart.cart_item_set.create(is_large = is_large, quantity = quantity, item = item)

        return HttpResponseRedirect("/menu")

    menu_items = Menu_item.objects.all()
    return render(request, "menu.html",{"menu_items": menu_items})

# Must be logged in to make an order
@login_required
def order(request):
    try:
        cart = Cart.objects.get(user = request.user)
    except ObjectDoesNotExist:
        return render(request, "order.html", {"cart": None})

    if request.method == "POST":
        order = Order.objects.create(user = request.user)

        order_lines = [Order_item(
            order = order,
            quantity = cart_item.quantity,
            is_large = cart_item.is_large,
            item = cart_item.item
            ) for cart_item in cart.cart_item_set.all()]

        print([line.description for line in order_lines])

        order.order_item_set.bulk_create(order_lines)
        Cart.objects.filter(id = cart.id).delete()
        return render(request, "ordered.html", {"order_id": order.id})

    return render(request, "order.html", {"cart": cart})

# Only staff should get to the list of orders
@staff_member_required
def orders(request):
    orders = Order.objects.all()

    return render(request, "admin/orders.html", {"orders": orders})

# From https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
def register(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            firstname = form.cleaned_data.get("firstname")
            lastname = form.cleaned_data.get("lastname")

            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            login(request, user)
            return render(request, "registration/registered.html")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})