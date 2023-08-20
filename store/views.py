from django.shortcuts import render, get_object_or_404
from .models import Products
from catagories.models import Category
from cart.views import _cart_id, CartItem
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.db.models import Q

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

    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,

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
