from django.views.generic import CreateView, ListView, DetailView
from .models import Order, OrderItem
from .forms import OrderCreateForm
from django.shortcuts import redirect
from django.urls import reverse
from products.models import ProductVariant
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from django.utils.dateparse import parse_date


@staff_member_required
def sales_report(request):
    # диапазон дат
    df = parse_date(request.GET.get('date_from')) or None
    dt = parse_date(request.GET.get('date_to')) or None

    qs = OrderItem.objects.select_related(
        'variant__product__seller'
    ).filter(order__paid=True)
    if df:
        qs = qs.filter(order__created_at__date__gte=df)
    if dt:
        qs = qs.filter(order__created_at__date__lte=dt)

    report = qs.values(
        seller_id=F('variant__product__seller__id'),
        seller_name=F('variant__product__seller__company_name')
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('variant__price'))
    ).order_by('-total_revenue')

    return render(request, 'orders/sales_report.html', {
        'report': report, 'date_from': df, 'date_to': dt
    })


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = 'orders/order_form.html'

    def form_valid(self, form):
        # Сохраняем сам заказ
        order = form.save(commit=False)
        order.buyer = self.request.user
        order.save()

        # Берём корзину из сессии и отфильтровываем некорректные ключи
        raw_cart = self.request.session.get('cart', {})
        clean_cart = {}
        for vid, qty in raw_cart.items():
            # пропускаем пустые ключи и те, что не состоят из цифр
            if not isinstance(vid, str) or not vid.isdigit():
                continue
            vid_int = int(vid)
            # qty тоже должно быть целым положительным
            try:
                qty_int = int(qty)
            except (ValueError, TypeError):
                continue
            if qty_int < 1:
                continue
            clean_cart[vid_int] = qty_int

        # Создаём OrderItem и уменьшаем склад
        for variant_id, quantity in clean_cart.items():
            try:
                variant = ProductVariant.objects.get(pk=variant_id)
            except ProductVariant.DoesNotExist:
                continue
            # если заказали больше, чем есть на складе, ограничиваем
            if quantity > variant.stock:
                quantity = variant.stock
            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=quantity
            )
            variant.stock -= quantity
            variant.save()

        # Очищаем корзину
        self.request.session['cart'] = {}

        # Переходим на страницу просмотра заказа
        return redirect(reverse('order_detail', args=[order.pk]))


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'

    def get_queryset(self):
        # гарантия, что никто чужой не увидит ваш заказ
        return Order.objects.filter(buyer=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # создаём список items с полем subtotal
        items_with_subtotals = []
        for item in self.object.items.select_related('variant'):
            subtotal = item.quantity * item.variant.price
            items_with_subtotals.append({
                'product_title': item.variant.product.title,
                'variant':        f"{item.variant.color} / {item.variant.size}",
                'price':          item.variant.price,
                'quantity':       item.quantity,
                'subtotal':       subtotal,
            })
        ctx['order_items'] = items_with_subtotals
        # передаём и общий total, если нужно
        ctx['order_total'] = sum(i['subtotal'] for i in items_with_subtotals)
        return ctx


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # показываем только заказы текущего пользователя, в обратном хронологическом порядке
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')

