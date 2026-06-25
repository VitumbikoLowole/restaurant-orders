from django.contrib import admin

from .models import MenuCategory, MenuItem, Customer, Order, OrderItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "item_count", "created_at")
    search_fields = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")
    list_select_related = ("category",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "phone", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_select_related = ("user",)


class OrderItemInline(admin.TabularInline):
    """Shows order lines on the Order edit page."""
    model = OrderItem
    extra = 1
    autocomplete_fields = ("menu_item",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
    list_select_related = ("customer", "customer__user")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalc_total()