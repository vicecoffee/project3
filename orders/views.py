from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from orders.models import Menu_item, Order, Order_item
from .forms import RegisterForm, AddItemForm
from django import forms

# Had to add prefix when putting form in dict with item to make sure the html worked
menu_items = [{ "item": item, "form": AddItemForm(item_model = item, prefix=item.id)} for item in Menu_item.objects.all()]

# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required
def menu(request, id = 0):
    if request.method == "POST":
        item = Menu_item.objects.get(id = id)

        if item is None:
            messages.error(
                    request, "Something went wrong.  Please double-check and try again."
                    )

            return HttpResponseRedirect("/menu")

        form = AddItemForm(request.POST, item_model = item, prefix = item.id)

        if form.is_valid():
            size = form.cleaned_data.get("size")
            quantity = form.cleaned_data.get("quantity")
            extras = form.cleaned_data.get("extras")
            toppings = form.cleaned_data.get("toppings")

            cart, created = Order.objects.get_or_create(user = request.user, status = Order.SHOPPING)

            line = cart.order_item_set.create(
                size = size if size is not None else Order_item.NA,
                quantity = quantity,
                item = item
                )
            if extras is not None:
                line.extras.set(extras)

            if toppings is not None:
                line.toppings.set(toppings)

            line.save()

            messages.success(
                request, "{} {} x{} added to your cart.".format(line.item.name, line.item.category, line.quantity)
                )
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            if [field.errors for field in form]:
                messages.error(
                    request, "Something went wrong.  Please double-check and try again."
                    )

        return HttpResponseRedirect("/menu")

    return render(request, "menu.html",{"menu_items": menu_items})

# Must be logged in to make an order
@login_required
def order(request):
    try:
        cart = Order.objects.get(user = request.user, status = Order.SHOPPING)
    except ObjectDoesNotExist:
        return render(request, "order.html", {"cart": None})

    if request.method == "POST":
        cart.status = Order.PLACED
        cart.save()
        return render(request, "ordered.html", {"order_id": cart.id})

    return render(request, "order.html", {"cart": cart})

# Only staff should get to the list of orders
@staff_member_required
def orders(request):
    orders = Order.objects.exclude(status = Order.SHOPPING)

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