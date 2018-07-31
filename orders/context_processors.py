from orders.models import Cart
from django.core.exceptions import ObjectDoesNotExist

# From https://docs.djangoproject.com/en/2.0/ref/templates/api/
def cart(request):
    user = request.user
    cart_count = 0
    if user.is_authenticated:
        try:
            cart = Cart.objects.get(user = user)
            cart_count = cart.cart_item_set.count()
        except ObjectDoesNotExist:
            cart_count = 0

    return {"global_cart_count": cart_count}