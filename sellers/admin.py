from django.contrib import admin
from .models import SellerProfile
from .utils import send_seller_approval_email

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_sellers']

    def approve_sellers(self, request, queryset):
        for profile in queryset:
            profile.is_approved = True
            profile.save()
            send_seller_approval_email(profile)
        self.message_user(request, 'Выбранные продавцы одобрены и уведомлены.')
