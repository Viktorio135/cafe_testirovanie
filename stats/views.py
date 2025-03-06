from django.views.generic import TemplateView
from django.db.models import Sum
from orders.models import Order, Table

class RevenueView(TemplateView):
    template_name = 'stats/revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Расчет выручки
        paid_orders = Order.objects.filter(status='paid')
        context['total_revenue'] = sum(order.total_price for order in paid_orders)

        # Расчет количества свободных и занятых столов
        occupied_tables = Table.objects.filter(order__status__in=['pending', 'ready']).distinct()
        free_tables = Table.objects.exclude(id__in=occupied_tables).distinct()

        context['occupied_tables_count'] = occupied_tables.count()
        context['free_tables_count'] = free_tables.count()

        return context
