from django.db import models
from django.conf import settings
from products.models import ProductVariant
from django.utils import timezone


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Ожидает оплаты'),
        ('paid',      'Оплачен'),
        ('shipped',   'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at    = models.DateTimeField(auto_now_add=True)
    address       = models.CharField(max_length=500)
    paid          = models.BooleanField(default=False)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    delivery_date = models.DateField(null=True, blank=True,
                                     help_text='Ориентировочная дата доставки')

    def __str__(self):
        return f"Заказ #{self.pk} — {self.get_status_display()}"

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant  = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
