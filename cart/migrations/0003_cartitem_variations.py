# Generated by Django 3.2.20 on 2023-08-17 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_rename_is_availiable_variation_is_active'),
        ('cart', '0002_alter_cart_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variations',
            field=models.ManyToManyField(blank=True, to='store.Variation'),
        ),
    ]
