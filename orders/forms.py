from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem, Table

class OrderForm(forms.ModelForm):
    """Форма для создания и редактирования заказа"""
    class Meta:
        # Метакласс для настройки формы
        model = Order
        fields = ['table', 'status'] # список полей которые будут отображаться

    def __init__(self, *args, **kwargs):
        """Конструктор формы для вывода только свободных столов"""
        super().__init__(*args, **kwargs) # вызов родительского init для первоначальной инициализации
        # Фильтруем столы, которые не заняты
        self.fields['table'].queryset = Table.objects.exclude(
            order__status__in=['pending', 'ready'] # фильтр чтобы список включал нужный нам статус
        ).distinct() # удаляем дубликаты



"""Форма для промежуточной модели врамках одного заказа"""
OrderItemFormSet = inlineformset_factory(
    Order, 
    OrderItem, 
    fields=('item', 'quantity'), 
    extra=1, 
    can_delete=True
)