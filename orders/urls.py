from django.urls import path
from .views import (
    OrderCreateView, OrderDetailView, OrderListView, sales_report
)
from .views import sales_report

urlpatterns = [
    path('create/',  OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('my-orders/', OrderListView.as_view(),    name='order_list'),
    path('report/',   sales_report,                name='sales_report'),
]
