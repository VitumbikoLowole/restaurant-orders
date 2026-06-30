from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum, F
from django.utils import timezone


class MenuCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "menu categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def item_count(self):
        return self.items.count()


class MenuItem(models.Model):
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.PROTECT,
        related_name="items",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    preparation_time = models.PositiveIntegerField(
        default=15, help_text="Estimated preparation time in minutes"
    )
    photo = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]
        unique_together = [("category", "name")]

    def __str__(self):
        return f"{self.name} (RWF{self.price})"


class Table(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        RESERVED = "reserved", "Reserved"

    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    table_status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.AVAILABLE
    )

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number} (seats {self.capacity})"


class Customer(models.Model):
    STAFF = "staff"
    CUSTOMER = "customer"
    ROLE_CHOICES = [(STAFF, "Staff"), (CUSTOMER, "Customer")]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer",
    )
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        full = self.user.get_full_name()
        return full or self.user.username

    @property
    def is_staff_member(self):
        return self.role == self.STAFF or self.user.is_staff or self.user.is_superuser


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        SERVED = "served", "Served"
        COMPLETED = "completed", "Completed"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=150, blank=True)
    special_instructions = models.TextField(blank=True)
    items = models.ManyToManyField(
        MenuItem,
        through="OrderItem",
        related_name="orders",
        blank=True,
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        name = self.customer_name or str(self.customer) if self.customer else "Walk-in"
        return f"Order #{self.pk} - {name} - RWF{self.total_price}"

    def recalc_total(self, save=True):
        aggregate = self.order_items.aggregate(
            total=Sum(F("quantity") * F("unit_price"))
        )
        self.total_price = aggregate["total"] or Decimal("0.00")
        if save:
            super().save(update_fields=["total_price"])
        return self.total_price


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_requests = models.TextField(blank=True)

    class Meta:
        unique_together = [("order", "menu_item")]

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price
