from .models import Cart, CartItem
from .views import _cart_id



def counter(request):
    count = 0
    cart = Cart.objects.filter(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart[:1])
    try:
        for cart_item in cart_items:
            count += cart_item.quantity
    except Cart.DoesNotExist:
        count = 0

    return dict(count=count)