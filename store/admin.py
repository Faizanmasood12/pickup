from django.contrib import admin
from .models import Products
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modefied', 'is_availiable')
    prepopulated_fields = {'slug':('product_name',)}

admin.site.register(Products, ProductAdmin)
