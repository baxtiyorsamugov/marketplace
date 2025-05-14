from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product_title', 'author', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'rating', 'product__seller')
    search_fields = ('product__title', 'author__username', 'text')
    list_editable = ('approved',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def product_title(self, obj):
        # Показываем поле title из связанного товара
        return obj.product.title
    product_title.short_description = 'Товар'
