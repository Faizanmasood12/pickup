import datetime
from .forms import OrderForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from cart.models import CartItem
from .models import Order, Payment, OrderProduct
import json
from store.models import Products
from django.core.mail import EmailMessage
from django.template.loader import render_to_string



# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # move cartitem to orderproduct table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.user_id = request.user.id
        orderproduct.payment = payment
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    # reduce the quantity of sold item
        product = Products.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # send order recieved email to user
    mail_subject = 'Order Recieved'
    message = render_to_string('orders/order_recieved_email.html',
                               {'user': request.user,
                                'order': order,
                                })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # send transiction id and order number back to submit through json format
    data = {
        'order': order.order_number,
        'transID': payment.payment_id
    }

    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_items_count = cart_items.count()
    if cart_items_count <= 0:
        return redirect('store')

    tax = 0
    grand_total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total / 100)
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phonenumber = form.cleaned_data['phonenumber']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()


            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d') # this will be in this format 20230826
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number )

            context = {
                'order': order,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'cart_items': cart_items
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')




def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    print("These are the order number and payment id ", order_number, '&', transID)

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        orderproducts = OrderProduct.objects.filter(order_id=order.id)
        print(f'this is tax{order.tax}')
        subtotal = 0
        for i in orderproducts:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)
        print(f'it enter in try fields and this is the payment:  {payment}' )

        context = {
            'order': order,
            'orderproducts':orderproducts,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,

        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        print('it enter in except fields.')
        return redirect('home')


# def payment_failed_view(request):
#     return render(request, 'orders/payment_failed.html')