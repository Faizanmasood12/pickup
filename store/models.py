from django.db import models
from catagories.models import Category
from django.urls import reverse

# Create your models here.
class Products(models.Model):
    """create model for products"""
    product_name =  models.CharField(max_length=200, unique=True)
    slug =          models.SlugField(max_length=200, unique=True)
    price =         models.FloatField()
    stock =         models.IntegerField()
    descriptions =  models.TextField(max_length=500)
    images =        models.ImageField(upload_to='photos/products')
    is_availiable = models.BooleanField(default=True)
    Date_created =  models.DateTimeField(auto_now_add=True)
    modefied =      models.DateTimeField(auto_now=True)
    category =      models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Products'

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


class Variation(models.Model):
    variation_category_choices = (
        ('color', 'color'),
        ('size', 'size')
    )
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200, choices=variation_category_choices)
    variation_value = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value