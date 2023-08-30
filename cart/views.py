from django.shortcuts import render, redirect, get_object_or_404
from store.models import Products, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.
def _cart_id(request):

        cart = request.session.session_key
        if not cart:
            cart = request.session.create()
        return cart




def add_cart(request, product_id):
    product = Products.objects.get(id=product_id)

    if request.user.is_authenticated:
        variation_product = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variations = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    variation_product.append(variations)
                except:
                    pass
        print(f'-------------------\nThese are product variations before checking item in user authenticated.\n{variation_product}\n---------------------')

        is_cart_item_exist = CartItem.objects.filter(product=product, user=request.user).exists()
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, user=request.user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(f'-------------------\nThese are product variations after checking items in user authenticated.\n{variation_product}\n---------------------')

            if variation_product in ex_var_list:  # so if variation product in existing variation we just increment product.
                index = ex_var_list.index(variation_product)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=request.user)
                if len(variation_product) > 0:
                    item.variations.clear()
                    item.variations.add(*variation_product)
                    item.save()

            return redirect('cart')

        else:
            item = CartItem.objects.create(
                product=product,
                quantity=1,
                user = request.user,
            )
            if len(variation_product) > 0:
                item.variations.clear()
                item.variations.add(*variation_product)
                item.save()
        return redirect('cart')

    else:
        variation_product = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                   variations = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                   variation_product.append(variations)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        print(f'-------------------\nThese are product variations before checking item.\n{variation_product}\n---------------------')
        is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(f'-------------------\nThese are product variations After checking item existing.\n{variation_product}\n---------------------')

            if variation_product in ex_var_list:# so if variation product in existing variation we just increment product.
                index = ex_var_list.index(variation_product)
                item_id = id[index]
                item = CartItem.objects.get(product=product, cart=cart, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity = 1, cart= cart)
                if len(variation_product) > 0:
                    item.variations.clear()
                    item.variations.add(*variation_product)
                    item.save()

            return redirect( 'cart' )

        else:
            item = CartItem.objects.create(
                product=product,
                quantity = 1,
                cart=cart,
            )
            if len(variation_product) > 0:
                item.variations.clear()
                item.variations.add(*variation_product)
                item.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Products, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except Cart.DoesNotExist:
        pass
    return redirect( 'cart' )

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Products, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()

    return redirect( 'cart' )


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    user = request.user
    try:

        if user.is_authenticated:
            cart_items = CartItem.objects.filter(user=user, is_availiable=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_availiable=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total/100)
        grand_total = total + tax
    except ObjectDoesNotExist :
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url = 'login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_availiable=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_availiable=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total / 100)
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'accounts/checkout.html', context)