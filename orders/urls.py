from django.urls import path

from .views import OrderListView, OrderCreateView, UpdateStatusView, DeleteOrderView, OrderUpdateView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path('order/update_status/<int:pk>/', UpdateStatusView.as_view(), name='order_edit'),
    path('order/delete/<int:pk>/', DeleteOrderView.as_view(), name='order_delete'),
    path("order/update/<int:pk>/", OrderUpdateView.as_view(), name="order_update"),
]
