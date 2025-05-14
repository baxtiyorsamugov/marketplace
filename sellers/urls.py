app_name = 'seller'

from django.urls import path
from .views import become_seller, seller_dashboard
from . import views

urlpatterns = [
    path('become/', become_seller, name='become_seller'),
    path('dashboard/', views.SellerDashboard.as_view(), name='dashboard'),
    path('products/', views.SellerProductList.as_view(), name='product_list'),
    path('products/add/', views.SellerProductCreate.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.SellerProductUpdate.as_view(), name='product_update'),
    path('products/<int:product_pk>/variant/add/', views.SellerVariantCreate.as_view(), name='variant_add'),
    path('stats/', views.SellerStats.as_view(), name='stats'),
    path('reviews/', views.SellerReviews.as_view(), name='review_list'),
    path('reviews/<int:pk>/reply/', views.SellerReviewUpdate.as_view(), name='review_reply'),
]
