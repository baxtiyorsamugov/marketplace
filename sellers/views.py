from django.shortcuts import render, redirect
from .forms import SellerProfileForm
from .models import SellerProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    View, TemplateView, ListView, CreateView, UpdateView, DetailView, FormView
)
from django.urls import reverse_lazy
from .mixins import SellerRequiredMixin
from products.models import Product, ProductVariant, Category
from products.forms import ProductForm, VariantForm, VariantFormSet
from orders.models import OrderItem
from reviews.models import Review
from reviews.forms import SellerResponseForm
from django.db.models import Sum, F, Count, Avg
from django.utils import timezone
import calendar
from django.http import JsonResponse


def ajax_load_subcategories(request):
    parent_id = request.GET.get('category')
    if not parent_id:
        return JsonResponse({'error': 'no category'}, status=400)

    subs = Category.objects.filter(parent_id=parent_id).order_by('name')
    data = [{'id': c.pk, 'name': c.name} for c in subs]
    return JsonResponse(data, safe=False)


# — Кабинет
class SellerDashboard(SellerRequiredMixin, TemplateView):
    template_name = 'sellers/dashboard.html'

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        profile = self.request.user.sellerprofile

        # ----- 1) данные по продажам (как было) -----
        now = timezone.now()
        one_year_ago = now.replace(year=now.year - 1)
        sales = (OrderItem.objects
                 .filter(variant__product__seller=profile, order__created_at__gte=one_year_ago)
                 .annotate(month=F('order__created_at__month'))
                 .values('month')
                 .annotate(total_qty=Sum('quantity'))
                 )
        months = [calendar.month_name[i] for i in range(1, 13)]
        sales_data = [0] * 12
        for s in sales:
            sales_data[s['month'] - 1] = s['total_qty']

        # ----- 2) stock-фильтр -----
        # читаем GET-параметр ?stock_below=...
        try:
            stock_below = int(self.request.GET.get('stock_below', ''))
        except ValueError:
            stock_below = None

        variants_qs = ProductVariant.objects.filter(product__seller=profile)
        if stock_below is not None:
            variants_qs = variants_qs.filter(stock__lte=stock_below)

        variants = variants_qs.values('id', 'product__title', 'color', 'size', 'stock')
        var_labels = [f"{v['product__title']} ({v['color']}/{v['size']})" for v in variants]
        var_stock = [v['stock'] for v in variants]

        # ----- 3) рейтинги (как было) -----
        ratings = (Review.objects
                   .filter(product__seller=profile, approved=True)
                   .values('product__title')
                   .annotate(avg_rating=Avg('rating'))
                   )
        prod_labels = [r['product__title'] for r in ratings]
        prod_rating = [round(r['avg_rating'], 2) for r in ratings]

        ctx.update({
            # для графика продаж
            'chart_months': months,
            'chart_sales': sales_data,
            # для графика остатков
            'chart_variants': var_labels,
            'chart_stock': var_stock,
            'stock_below': stock_below,
            # для графика рейтингов
            'chart_products': prod_labels,
            'chart_ratings': prod_rating,
        })

        ctx['sales_count'] = OrderItem.objects.filter(
            variant__product__seller=profile
        ).aggregate(total=Sum('quantity'))['total'] or 0
        ctx['revenue'] = OrderItem.objects.filter(
            variant__product__seller=profile
        ).aggregate(
            revenue=Sum(F('quantity')*F('variant__price'))
        )['revenue'] or 0
        return ctx


# — Список и создание товаров
class SellerProductList(SellerRequiredMixin, ListView):
    template_name = 'sellers/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user.sellerprofile)


class SellerProductCreate(SellerRequiredMixin, CreateView):
    template_name = 'sellers/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('seller:product_list')

    def form_valid(self, form):
        form.instance.seller = self.request.user.sellerprofile
        return super().form_valid(form)


class SellerProductUpdate(SellerRequiredMixin, View):
    template_name = 'sellers/product_form.html'
    success_url   = reverse_lazy('seller:product_list')

    def dispatch(self, request, *args, **kwargs):
        # получаем объект или 404
        self.product = Product.objects.filter(
            pk=kwargs['pk'],
            seller=request.user.sellerprofile
        ).first()
        if not self.product:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form    = ProductForm(instance=self.product)
        formset = VariantFormSet(instance=self.product)
        return render(request, self.template_name, {
            'form': form,
            'variant_formset': formset
        })

    def post(self, request, *args, **kwargs):
        form    = ProductForm(request.POST, instance=self.product)
        formset = VariantFormSet(
            request.POST, request.FILES,
            instance=self.product
        )

        # Выведем в консоль ошибки, чтобы точно увидеть, в чём проблема
        if not form.is_valid():
            print('=== ProductForm errors ===', form.errors)
        if not formset.is_valid():
            print('=== VariantFormSet errors ===', formset.errors)

        if form.is_valid() and formset.is_valid():
            # Сохраняем сам товар
            product = form.save(commit=False)
            product.seller = request.user.sellerprofile
            product.save()

            # Сохраняем варианты поштучно
            variants = formset.save(commit=False)
            for variant in variants:
                variant.product = product
                variant.save()
            # Удаляем помеченные на удаление
            for variant in formset.deleted_objects:
                variant.delete()

            return redirect(self.success_url)

        # если не валидно — заново рендерим форму с ошибками
        return render(request, self.template_name, {
            'form': form,
            'variant_formset': formset
        })

# — Управление вариантами
class SellerVariantCreate(SellerRequiredMixin, CreateView):
    template_name = 'sellers/variant_form.html'
    form_class = VariantForm

    def dispatch(self, request, *a, **kw):
        self.product = Product.objects.get(pk=kw['product_pk'], seller=request.user.sellerprofile)
        return super().dispatch(request, *a, **kw)

    def form_valid(self, form):
        form.instance.product = self.product
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('seller:product_update', args=[self.product.pk])


# — Статистика по товару
class SellerStats(SellerRequiredMixin, TemplateView):
    template_name = 'sellers/stats.html'

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        profile = self.request.user.sellerprofile
        stats = OrderItem.objects.filter(
            variant__product__seller=profile
        ).values(
            'variant__product__title'
        ).annotate(
            sold=Sum('quantity'),
            revenue=Sum(F('quantity')*F('variant__price'))
        )
        ctx['stats'] = stats
        return ctx


# — Отзывы продавцу
class SellerReviews(SellerRequiredMixin, ListView):
    template_name = 'sellers/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return Review.objects.filter(product__seller=self.request.user.sellerprofile)


class SellerReviewUpdate(SellerRequiredMixin, UpdateView):
    template_name = 'sellers/review_form.html'
    form_class = SellerResponseForm
    success_url = reverse_lazy('seller:review_list')

    def get_queryset(self):
        return Review.objects.filter(product__seller=self.request.user.sellerprofile)



@login_required
def become_seller(request):
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Заявка отправлена, ожидайте одобрения.')
            return redirect('seller_dashboard')
    else:
        form = SellerProfileForm()
    return render(request, 'sellers/become_seller.html', {'form': form})

@login_required
def seller_dashboard(request):
    profile = SellerProfile.objects.filter(user=request.user, is_approved=True).first()
    return render(request, 'sellers/dashboard.html', {'profile': profile})
