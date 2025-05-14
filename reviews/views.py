from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from .forms import ReviewForm
from .models import Review
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin


class ReviewCreateView(LoginRequiredMixin, View):
    def get(self, request, product_pk):
        form = ReviewForm()
        return render(request, 'reviews/review_form.html', {'form': form})

    def post(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.product = product
            rev.author = request.user
            rev.save()
            return redirect('product_detail', pk=product_pk)
        return render(request, 'reviews/review_form.html', {'form': form})
