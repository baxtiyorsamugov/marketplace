from django.contrib import admin
from .models import Category, Product, ProductVariant

admin.site.register(Category)
admin.site.register(Product)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display   = ('variant_name', 'price', 'stock')
    list_filter    = ('product__seller', 'price', 'stock')
    search_fields  = ('product__title', 'color', 'size')
    list_editable  = ('price', 'stock')

    def variant_name(self, obj):
        return str(obj)   # использует ваш __str__
    variant_name.short_description = 'Вариант'
