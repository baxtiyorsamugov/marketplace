from django.views.generic import ListView, DetailView
from .models import Product, ProductVariant, Category, Favorite
from django.db.models import Prefetch
from django.shortcuts import redirect, render, reverse
from django.urls import reverse
from django_filters.views import FilterView
from .filters import ProductFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


class WishlistView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'products/wishlist.html'
    context_object_name = 'favorites'
    paginate_by = 12

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('product')


@login_required
def toggle_favorite(request, pk):
    """
    AJAX или POST: если нет — добавляем в избранное, если есть — удаляем.
    Возвращает JSON {'status': 'added'|'removed'}.
    """
    product = Product.objects.get(pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        status = 'removed'
    else:
        status = 'added'
    return JsonResponse({'status': status})


class ProductListView(FilterView):
    model = Product
    paginate_by = 12
    template_name = 'products/product_list.html'
    filterset_class = ProductFilter

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        if self.request.user.is_authenticated:
            # забираем все PK товаров в избранном у текущего юзера
            fav_ids = self.request.user.favorites.values_list('product_id', flat=True)
            ctx['user_favorites'] = set(fav_ids)
        else:
            ctx['user_favorites'] = set()
        return ctx

    # def get_context_data(self, **kwargs):
    #     ctx = super().get_context_data(**kwargs)
    #     ctx['categories'] = Category.objects.filter(parent__isnull=True)
    #     return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # ctx['object'] — это ваш Product
        seller_profile = self.object.seller
        ctx['seller'] = seller_profile
        ctx['variants'] = self.object.variants.all()
        ctx['approved_reviews'] = self.object.reviews.filter(approved=True)
        ctx['star_range'] = range(1, 6)
        return ctx


def cart_add(request):
    variant_id = request.POST.get('variant')
    qty = request.POST.get('quantity')
    # Проверяем, что variant_id и qty – числа
    if not variant_id or not qty or not variant_id.isdigit() or not qty.isdigit():
        return redirect(reverse('product_list'))
    variant_id = int(variant_id)
    qty = int(qty)

    # Проверим, что такой вариант существует и что хватает на складе
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return redirect(reverse('product_list'))
    if qty < 1 or qty > variant.stock:
        return redirect(reverse('product_detail', args=[variant.product.pk]))

    # Всё ок, кладём в сессию
    cart = request.session.get('cart', {})
    cart[variant_id] = cart.get(variant_id, 0) + qty
    request.session['cart'] = cart

    return redirect('cart_detail')


def cart_remove(request, variant_id):
    """Удалить вариант из корзины."""
    cart = request.session.get('cart', {})
    if variant_id in cart:
        del cart[variant_id]
        request.session['cart'] = cart
    return redirect('cart_detail')


def cart_detail(request):
    """Показать содержимое корзины, пропуская некорректные ключи."""
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for vid, qty in cart.items():
        # фильтруем пустые или нечисловые ключи
        try:
            variant_pk = int(vid)
        except (ValueError, TypeError):
            continue

        try:
            variant = ProductVariant.objects.get(pk=variant_pk)
        except ProductVariant.DoesNotExist:
            continue

        subtotal = variant.price * qty
        total += subtotal
        items.append({
            'variant': variant,
            'quantity': qty,
            'subtotal': subtotal,
        })

    return render(request, 'cart_detail.html', {
        'items': items,
        'total': total,
    })
