from django.urls import path

from .views import RevenueView

app_name = 'stats'

urlpatterns = [
    path('', RevenueView.as_view(), name='revenue'),
]
