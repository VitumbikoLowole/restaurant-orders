from rest_framework import serializers
from .models import MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    # category_name is read-only, pulled across the FK with source=
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price",
                  "category", "category_name", "is_available", "photo"]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["menu_item", "menu_item_name", "quantity", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    # customer_name is the model field (stored text, e.g. "John Doe").
    # customer_display is a computed fallback for walk-in orders.
    customer_display = serializers.SerializerMethodField()
    lines = OrderItemSerializer(source="order_items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "customer", "customer_name", "customer_display",
            "status", "total_price", "created_at", "lines",
        ]

    def get_customer_display(self, obj):
        if obj.customer:
            return str(obj.customer)
        return obj.customer_name or "Walk-in"