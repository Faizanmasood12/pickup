from django.shortcuts import render, get_object_or_404, redirect
from .models import Products, ReviewRating
from catagories.models import Category
from cart.views import _cart_id, CartItem
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReveiwForm
from django.contrib import messages
from orders.models import OrderProduct


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Products.objects.all().filter(category=categories, is_availiable=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Products.objects.all().filter(is_availiable=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Products.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated: # check user login and fix anonymus user
        # fetch ordered product  for submit button to show when product is purchased
        try:
            ordered_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            ordered_product = None

        # fetch product in cart for redirecting to cart or checkout
        try:
            cart_product = CartItem.objects.filter(user=request.user, product_id=single_product.id).exists()
        except CartItem.DoesNotExist:
            cart_product = None
    else:
        ordered_product = None
        cart_product = None

    # fetch the reviews the all reviews to show on product
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)


    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'ordered_product': ordered_product,
        'cart_product': cart_product,
        'reviews': reviews,

    }
    return render(request, 'store/product_detail.html', context)


def search(request, products=None, product_count=None):

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword.strip():
            products = Products.objects.order_by("-Date_created").filter(Q(descriptions__icontains=keyword)
            | Q(product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReveiwForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Thanks! you're review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReveiwForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.user_id = request.user.id
                data.product_id = product_id
                data.save()
                messages.success(request, "Thanks! You're review has been submitted.")
                return redirect(url)