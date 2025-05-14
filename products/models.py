from django.db import models
from sellers.models import SellerProfile
from django.conf import settings

class Favorite(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='favorites')
    product   = models.ForeignKey('Product',
                                  on_delete=models.CASCADE,
                                  related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ❤ {self.product.title}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # теперь везде, где Django будет приводить Product к строке,
        # он покажет его title, а не "Product object (pk)"
        return self.title


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        # возвращает: "<название товара> — <цвет> / <размер>"
        return f'{self.product.title} — {self.color} / {self.size}'

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image   = models.ImageField(upload_to='products/main_images/')
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
