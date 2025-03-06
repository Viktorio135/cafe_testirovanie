import json


from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView
from django.views import View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Sum


from .models import Order
from .forms import OrderForm, OrderItemFormSet



"""Обработка ошибок"""
def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)




class OrderListView(ListView):
    """Страница со всеми заказами"""

    template_name = 'orders/order_list.html' 
    model = Order

    def get_queryset(self):
        """
        Изменяем родительский get_queryset для применения фильтрации 
        (изменение запроса, чтобы в  контекст передавались корекстные данные из БД)
        """

        # вызываем метод родительского класса для получения дэфолтного queryset
        queryset = super().get_queryset()
        # получаем параметры
        status = self.request.GET.get('status')
        search_query = self.request.GET.get('q', '').strip()
        search_type = self.request.GET.get('search_type', 'table')

        # Фильтруем по заданным параметрам
        if status:
            queryset = queryset.filter(status=status)

        if search_query:
            if search_type == 'table':
                # Проверка включает ли параметр номер стола
                queryset = queryset.filter(table__number__icontains=search_query)
            else:
                queryset = queryset.filter(id=search_query)
        else:
            queryset = queryset.all()

        return queryset

    def get_context_data(self, **kwargs):
        """Переопределение метода для отправки данных в шаблон"""

        # вызываем метод родительского класса для получения системных данных контекста
        context = super().get_context_data(**kwargs)
        context["status_choices"] = [
            ("pending", "В ожидании"),
            ("ready", "Готово"),
            ("paid", "Оплачено")
        ]
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context
    

class OrderCreateView(CreateView):
    """Создание заказа"""

    model = Order
    form_class = OrderForm
    template_name = 'orders/order_create.html'
    success_url = reverse_lazy('orders:order_list')

    def get_context_data(self, **kwargs):
        """Переопределение метода для отправки данных в шаблон"""

        # вызываем метод родительского класса для получения системных данных контекста
        context = super().get_context_data(**kwargs)
        # проверяем делался ли запрос до этого (например для вывода ошибко) и передает в него форму
        if self.request.POST:
            context['order_item_formset'] = OrderItemFormSet(self.request.POST)
        else:
            context['order_item_formset'] = OrderItemFormSet()
        return context

    def form_valid(self, form):
        """Проверям корректна ли форма"""

        context = self.get_context_data() # получаем контекст для шаблона
        order_item_formset = context['order_item_formset']
        
        # Проверяем, что стол свободен
        table = form.cleaned_data['table']
        if Order.objects.filter(table=table, status__in=['pending', 'ready']).exists():
            return self.render_to_response(self.get_context_data(form=form))

        # проверка коррекстности данных в формах
        if form.is_valid() and order_item_formset.is_valid():
            self.object = form.save()
            order_item_formset.instance = self.object  # Привязываем formset к заказу
            order_item_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form)) # указываем неккоректные данные 
        

class UpdateStatusView(View):
    """Обновление статуса заказа"""

    def post(self, request, pk):
        try:
            order = get_object_or_404(Order, id=pk) # получаем объект Order, иначе Not Found
            # так как запрос передается в body в формате строки JSON, его необходимо декодироваь, потом преобразовать в словарь
            body = request.body.decode('utf-8')
            data = json.loads(body)

            new_status = data.get("status")
            if not new_status:
                # ошибка в случае некорректного статуса
                return JsonResponse({'success': False, 'error': 'Status is required.'}, status=400)

            # Проверка допустимости нового статуса
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if new_status not in valid_statuses:
                # ошибка в случае некорректного статуса
                return JsonResponse({'success': False, 'error': 'Invalid status.'}, status=400)

            order.status = new_status
            order.save() #сохраняем изменения

            # Ответ в jsno формате, чтобы JS из шаблона понимал статус запроса
            return JsonResponse({
                'success': True,
                'new_status': order.get_status_display()
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        

class DeleteOrderView(View):
    """Удаление заказа"""

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        order.delete() # если объект найден, удаляем его

        return redirect('orders:order_list') # перенаправляем на главную страницу
    

class OrderUpdateView(UpdateView):
    """Изменени заказа"""

    model = Order
    form_class = OrderForm
    template_name = 'orders/order_update.html'
    success_url = reverse_lazy('orders:order_list')

    def get_context_data(self, **kwargs):
        """Переопределение метода для отправки данных в шаблон"""

        # вызываем метод родительского класса для получения системных данных контекста
        context = super().get_context_data(**kwargs)
        # всё аналогично представлению для создания заказа
        if self.request.POST:
            context['order_item_formset'] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            context['order_item_formset'] = OrderItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        order_item_formset = context['order_item_formset']

        if form.is_valid() and order_item_formset.is_valid():
            self.object = form.save()
            order_item_formset.instance = self.object
            order_item_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))