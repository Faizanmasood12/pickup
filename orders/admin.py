from django.contrib import admin
from .models import Payment, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ['payment', 'user', 'quantity', 'product', 'product_price']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phonenumber', 'email', 'city', 'order_total', 'is_ordered','created_at', 'status' ]
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phonenumber', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)