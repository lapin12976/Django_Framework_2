import ordersapp.views as ordersapp
from django.urls import path

app_name = "ordersapp"

urlpatterns = [
    path(r'', ordersapp.OrderList.as_view(), name='list'),
    path(r'create/', ordersapp.OrderCreate.as_view(), name='create'),
    path(r'update/<pk>/', ordersapp.OrderUpdate.as_view(), name='update'),
    path(r'delete/<pk>/', ordersapp.OrderDelete.as_view(), name='delete'),
    path(r'read/(<pk>/', ordersapp.OrderRead.as_view(), name='read'),
    path(r'forming/complete/<pk>/', ordersapp.forming_complete, name='forming_complete'),
]
