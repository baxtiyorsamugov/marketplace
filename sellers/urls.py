app_name = 'seller'

from django.urls import path
from .views import become_seller, seller_dashboard
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('become/', become_seller, name='become_seller'),
    path('login/', auth_views.LoginView.as_view(
        template_name='sellers/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='sellers/logged_out.html',
        next_page='seller:login'  # после выхода перебросит на seller:login
    ), name='logout'),
    path('dashboard/', views.SellerDashboard.as_view(), name='dashboard'),
    path('products/', views.SellerProductList.as_view(), name='product_list'),
    path('products/add/', views.SellerProductCreate.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.SellerProductUpdate.as_view(), name='product_update'),
    path('products/<int:product_pk>/variant/add/', views.SellerVariantCreate.as_view(), name='variant_add'),
    path('stats/', views.SellerStats.as_view(), name='stats'),
    path('reviews/', views.SellerReviews.as_view(), name='review_list'),
    path('reviews/<int:pk>/reply/', views.SellerReviewUpdate.as_view(), name='review_reply'),
    path(
        'ajax/subcategories/',
        views.ajax_load_subcategories,
        name='ajax_load_subcategories'
    )
]
