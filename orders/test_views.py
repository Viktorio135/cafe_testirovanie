import pytest
from django.urls import reverse
from rest_framework import status
from orders.models import Order, Table, Item, OrderItem

@pytest.mark.django_db
def test_order_list(client):
    url = reverse('orders:order_list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_order_create(client):
    # Создаем необходимые объекты
    table = Table.objects.create(number=1, capacity=4)
    item = Item.objects.create(name="Pizza", price=10.00)
    
    # URL для создания заказа
    url = reverse('orders:order_create')
    
    # Данные для POST-запроса c данными для формы
    data = {
        'table': table.id,
        'status': 'pending',
        'orderitem_set-TOTAL_FORMS': '1',  # Количество форм в формсете
        'orderitem_set-INITIAL_FORMS': '0',
        'orderitem_set-0-item': item.id,
        'orderitem_set-0-quantity': 2,
    }
    
    response = client.post(url, data)
    
    assert response.status_code == 302  # Ожидаем редирект
    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1
    
    # Проверяем, что заказ корректно связан с элементами
    order = Order.objects.first()
    assert order.table == table
    assert order.orderitem_set.first().quantity == 2
    assert order.total_price == 20.00

    data = {
        'table': table.id,
        'status': 'pending',
        'orderitem_set-TOTAL_FORMS': '1',  # Количество форм в формсете
        'orderitem_set-INITIAL_FORMS': '0',
        'orderitem_set-0-item': item.id,
        'orderitem_set-0-quantity': 2,
    }
    
    response = client.post(url, data)

    assert response.status_code == 200 # Проверяем что создание не срабатывает при дублировании стола