from rest_framework import serializers
from orders.models import Order, OrderItem, Item, Table

class OrderItemSerializer(serializers.ModelSerializer):
    """Промежуточный сериалайзер для OrderItem"""
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all()) # Поле для обозначения отношений с Item

    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='orderitem_set')  # Используем обратное отношение
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all()) # Поле для обозначения отношений с Table


    class Meta:
        model = Order
        fields = ['id', 'table', 'status', 'items', 'total_price']

    total_price = serializers.SerializerMethodField() # Кастомное поле для рассчета общей суммы

    def get_total_price(self, obj):
        return obj.total_price

    def create(self, validated_data):
        items_data = validated_data.pop('orderitem_set')
        order = Order.objects.create(**validated_data)
        """Создание записей в промежуточной таблице"""
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        """Обновление заказа"""
        # Получение и схоранение данных из формы
        items_data = validated_data.pop('orderitem_set', [])
        instance.table = validated_data.get('table', instance.table)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Обновляем OrderItem
        existing_items = {item.id: item for item in instance.orderitem_set.all()} # Уже созданные объекты
        for item_data in items_data:
            item_id = item_data.get('id', None)
            if item_id and item_id in existing_items:
                OrderItem.objects.filter(id=item_id).update(**item_data)
            else:
                OrderItem.objects.create(order=instance, **item_data)
        
        # Удаляем лишние элементы
        item_ids = [item.get('id') for item in items_data if item.get('id')]
        for item_id in existing_items:
            if item_id not in item_ids:
                OrderItem.objects.filter(id=item_id).delete()

        return instance