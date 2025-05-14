# products/filters.py

import django_filters
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(
        field_name='variants__price',
        lookup_expr='gte',
        label='Цена от'
    )
    price_max = django_filters.NumberFilter(
        field_name='variants__price',
        lookup_expr='lte',
        label='Цена до'
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Категория'
    )

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max']
