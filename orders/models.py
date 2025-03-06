from django.db import models


class Item(models.Model):
    """Блюда"""
    name = models.CharField(verbose_name='Название блюда', max_length=150)
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        """Метод для изменения оображения объекта модели"""
        return f"#{self.id} {self.name} ({self.price} руб.)"
    
    class Meta:
        """Изменение абстрактного класса для улучшения читабельности таблицы в админке"""
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'


class OrderItem(models.Model):
    """Промежуточная таблица для связи ManyToMany"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    #рассчет суммы определенного товара
    @property
    def total_price(self):
        """метод-свойство для подсчета суммы блюда"""
        print(self.item.price * self.quantity)
        return self.item.price * self.quantity
    
    
    def __str__(self):
        """Метод для изменения оображения объекта модели"""
        return f'{self.order} - {self.item}'


class Table(models.Model):
    """Столы"""
    number = models.IntegerField(
        verbose_name="Номер стола",
        unique=True
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
        default=2
    )
    description = models.CharField(
        verbose_name="Описание",
        max_length=200,
        blank=True
    ) #чтобы оставить заметку (например, "у окна")

    def __str__(self):
        """Метод для изменения оображения объекта модели"""
        return f"Стол #{self.number}"

    class Meta:
        """Изменение абстрактного класса для улучшения читабельности таблицы в админке"""
        verbose_name = "Стол"
        verbose_name_plural = "Столы"


class Order(models.Model):
    """Заказы"""
    STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("ready", "Готово"),
        ("paid", "Оплачено")
    ]
    table = models.ForeignKey(
        Table,
        verbose_name="Стол",
        on_delete=models.CASCADE,
    )
    items = models.ManyToManyField(
        Item, 
        through=OrderItem,  # Явное указание промежуточной модели
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    #Рассчет общей суммы заказа
    @property
    def total_price(self):
        """метод-свойство для подсчета суммы в промежуточной таблице"""
        return sum(
            order_item.total_price 
            for order_item in self.orderitem_set.all()  # Используем обратную связь
        )
    
    def __str__(self):
        """Метод для изменения оображения объекта модели"""
        return f"Заказ #{self.id} (Стол {self.table.number})"

    class Meta:
        """Изменение абстрактного класса для улучшения читабельности таблицы в админке"""
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

