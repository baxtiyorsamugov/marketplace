from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class SellerRequiredMixin(UserPassesTestMixin):
    """Проверяет, что пользователь — продавец и его профиль одобрен."""
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and \
               hasattr(user, 'sellerprofile') and \
               user.sellerprofile.is_approved

    def handle_no_permission(self):
        return redirect('products:product_list')
