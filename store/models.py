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