from django.urls import path
from .views import ReviewCreateView

urlpatterns = [
    path('add/<int:product_pk>/', ReviewCreateView.as_view(), name='review_add'),
]
