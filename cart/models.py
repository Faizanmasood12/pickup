from django.db import models
from store.models import Products, Variation


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Cart'

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    is_availiable = models.BooleanField(default=True)
    quantity = models.IntegerField()

    def sub_total(self):
        total = self.product.price * self.quantity
        return total

    def __unicode__(self):
        return self.product