from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('orders.urls')),
    path("statistics/", include('stats.urls')),
    path("api/", include('api.urls')),
]
    

handler404 = 'orders.views.custom_404_view'
handler400 = 'orders.views.custom_400_view'
