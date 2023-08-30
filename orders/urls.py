from django.urls import path, include
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),

    # payments success url
    path('order_complete/', views.order_complete, name='order_complete'),
    # paymets failed url
    # path('payment_failed/', views.payment_failed_view, name='payment_failed'),
]