import pytest
from orders.models import Order, Table, Item, OrderItem

@pytest.mark.django_db
def test_order_creation():
    # Создаем нужные объекты
    table = Table.objects.create(number=1, capacity=4)
    item = Item.objects.create(name="Пицца", price=10.00)
    
    # Создаем заказ
    order = Order.objects.create(table=table, status="pending")
    
    # Создаем связь через промежуточную модель
    order_item = OrderItem.objects.create(order=order, item=item, quantity=2)
    # Проверки
    assert order_item.quantity == 2
    assert order.table == table
    assert order.status == "pending"
    assert order.items.count() == 1
    assert float(order.total_price) == 20.00

@pytest.mark.django_db
def test_item_creation():
    item = Item.objects.create(name="Бургер", price=8.00)
    assert item.name == "Бургер"
    assert item.price == 8.00
