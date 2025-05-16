from django.urls import path
from .views import ProductListView, ProductDetailView, WishlistView, toggle_favorite
from .views import cart_add, cart_remove, cart_detail, get_subcategories
from . import views


urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/', cart_add, name='cart_add'),
    path('cart/remove/<int:variant_id>/', cart_remove, name='cart_remove'),
    path('wishlist/', views.WishlistView.as_view(),      name='wishlist'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('ajax/get-subcats/', views.get_subcategories, name='ajax_get_subcats'),

]
