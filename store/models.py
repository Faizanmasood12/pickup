from django.db import models
from catagories.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count

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

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
            return avg
    def reviewCount(self):
        reviewscounts = ReviewRating.objects.filter(product=self, status=True).aggregate(counts=Count('id'))
        count = 0
        if reviewscounts['counts'] is not None:
            count = int(reviewscounts['counts'])
            return count

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


class ReviewRating(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    rating = models.FloatField()
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject