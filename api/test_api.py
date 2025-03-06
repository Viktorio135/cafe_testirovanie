import pytest
from rest_framework import status
from rest_framework.test import APIClient
from orders.models import Item, Table, Order, OrderItem

@pytest.fixture
def api_client():
    """Фикстура для клиента API"""
    return APIClient()

@pytest.fixture
def table():
    """Фикстура для создания стола"""
    table = Table.objects.create(number=1, capacity=4, description="У окна")
    return table

@pytest.fixture
def item():
    """Фикстура для создания блюда"""
    item = Item.objects.create(name="Пицца", price=250.00)
    return item

@pytest.fixture
def order(table, item):
    """Фикстура для создания заказа"""
    order = Order.objects.create(table=table, status="pending")
    OrderItem.objects.create(order=order, item=item, quantity=2)
    return order

@pytest.mark.django_db
def test_get_orders(api_client, order):
    """Тест для получения всех заказов"""
    response = api_client.get('/api/orders/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['table'] == order.table.number
    assert response.data[0]['status'] == order.status
    assert response.data[0]['total_price'] == float(order.total_price)

@pytest.mark.django_db
def test_create_order(api_client, table, item):
    """Тест для создания нового заказа"""
    data = {
        "table": table.id,
        "status": "pending",
        "items": [
            {
                "item": item.id,
                "quantity": 2
            }
        ]
    }
    response = api_client.post('/api/orders/', data, format='json')

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_order_item_total_price(api_client, order, item):
    """Тест для проверки расчета общей суммы товара в заказе"""
    order_item = OrderItem.objects.get(order=order, item=item)
    assert order_item.total_price == item.price * order_item.quantity

@pytest.mark.django_db
def test_order_serializer(api_client, order):
    """Тест для сериализатора заказа"""
    response = api_client.get(f'/api/orders/{order.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == order.id
    assert response.data['table'] == order.table.number
    assert response.data['status'] == order.status
    assert 'items' in response.data
    assert 'total_price' in response.data

@pytest.mark.django_db
def test_update_order_status(api_client, order):
    """Тест для обновления статуса заказа"""
    new_status = "ready"
    response = api_client.patch(f'/api/orders/{order.id}/', {'status': new_status}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == new_status

@pytest.mark.django_db
def test_delete_order(api_client, order):
    """Тест для удаления заказа"""
    response = api_client.delete(f'/api/orders/{order.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Order.objects.filter(id=order.id).exists()