from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    # куда по умолчанию уходит покупатель
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # если у пользователя есть профиль продавца и он одобрен — в кабинет
        if hasattr(user, 'sellerprofile') and user.sellerprofile.is_approved:
            return reverse_lazy('seller:dashboard')
        # иначе — в каталог товаров
        return reverse_lazy('product_list')
