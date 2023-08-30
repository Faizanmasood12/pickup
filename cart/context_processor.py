from .models import Cart, CartItem
from .views import _cart_id



def counter(request):

    count = 0
    cart = Cart.objects.filter(cart_id=_cart_id(request))
    if request.user.is_authenticated:
        cart_items = CartItem.objects.all().filter(user=request.user)
    else:
        cart_items = CartItem.objects.all().filter(cart=cart[:1])
    try:
        for cart_item in cart_items:
            count += cart_item.quantity
    except Cart.DoesNotExist:
        count = 0

    return dict(count=count)