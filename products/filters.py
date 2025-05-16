# products/filters.py
import django_filters
from django.db.models import Q
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    # 1) Переопределяем filter для поля "category", чтобы он искал и в подкатегориях
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        method='filter_by_category_or_sub',
        label='Категория'
    )
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

    def filter_by_category_or_sub(self, queryset, name, value):
        # OR: либо категория = value, либо subcategory = value
        return queryset.filter(
            Q(category=value) | Q(subcategory=value)
        )

    class Meta:
        model  = Product
        fields = ['category', 'price_min', 'price_max']
