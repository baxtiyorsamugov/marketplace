from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductImage

from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('indented_name', 'parent',)
    list_filter = ('parent',)
    search_fields = ('name',)

    def indented_name(self, obj):
        # если есть родитель — отступаем
        level = 0
        p = obj.parent
        while p:
            level += 1
            p = p.parent
        return '  ' * level + obj.name
    indented_name.short_description = 'Название'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'subcategory', 'seller',)
    list_filter = ('category', 'subcategory',)
    search_fields = ('title',)
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {
            'fields': (
                'seller',
                ('category', 'subcategory'),
                'title', 'description',
            )
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('variant_name', 'price', 'stock')
    list_filter = ('product__seller', 'price', 'stock')
    search_fields = ('product__title', 'color', 'size')
    list_editable = ('price', 'stock')

    def variant_name(self, obj):
        return str(obj)   # использует ваш __str__
    variant_name.short_description = 'Вариант'
