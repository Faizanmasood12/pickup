from django.http import HttpResponse
from django.shortcuts import render
from store.models import Products

def home(request):
    products = Products.objects.all().filter(is_availiable=True)
    products_count = products.count()

    context = {'products': products, "products_count": products_count}
    return render(request, "home.html", context)