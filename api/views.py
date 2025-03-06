from rest_framework.viewsets import ModelViewSet
from orders.models import Order, Item
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


