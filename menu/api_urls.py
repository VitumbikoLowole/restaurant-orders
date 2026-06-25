from django.urls import path
from . import api_views

urlpatterns = [
    path("menu-items/", api_views.MenuItemListCreateAPI.as_view(), name="api_menu_items"),
    path("orders/today/", api_views.TodaysOrdersAPI.as_view(), name="api_orders_today"),
]