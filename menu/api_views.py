from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MenuItem, Order
from .serializers import MenuItemSerializer, OrderSerializer


class MenuItemListCreateAPI(generics.ListCreateAPIView):
    """
    GET  /api/menu-items/  → list all items as JSON
    POST /api/menu-items/  → create a new item from JSON body
    ListCreateAPIView gives you both in one class.
    """
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        return MenuItem.objects.select_related("category").order_by("name")


class TodaysOrdersAPI(APIView):
    """GET /api/orders/today/ → all orders created today, with nested lines."""

    def get(self, request):
        today = timezone.localdate()
        orders = (
            Order.objects.filter(created_at__date=today)
            .select_related("customer", "customer__user")
            .prefetch_related("order_items__menu_item")
            .order_by("-created_at")
        )
        data = OrderSerializer(orders, many=True).data
        return Response({"date": str(today), "count": len(data), "orders": data})