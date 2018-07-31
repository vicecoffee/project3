from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("menu/", views.menu, name="menu"),
    path("order/", views.order, name="order"),
    path("admin/view_orders/", views.orders, name="admin order list"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register")
]
