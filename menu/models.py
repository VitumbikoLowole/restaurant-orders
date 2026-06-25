from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum, F
from django.utils import timezone


class MenuCategory(models.Model):
    """
    A grouping of menu items, e.g. "Starters", "Mains", "Drinks".
    This is the "1" side of the Category -> Items one-to-many relationship.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "menu categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def item_count(self):
        # self.items is the reverse accessor created by related_name="items"
        # on MenuItem.category. It lets us count without writing any SQL.
        return self.items.count()


class MenuItem(models.Model):
    """
    A single dish or drink.

    RELATIONSHIP: ForeignKey to MenuCategory.
    Many items belong to one category (many-to-one).
    related_name="items" creates category.items as a reverse accessor,
    so from any category you can call category.items.all() to get its dishes.
    on_delete=PROTECT means you cannot delete a category that still has items.
    """
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.PROTECT,
        related_name="items",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    photo = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]
        unique_together = [("category", "name")]

    def __str__(self):
        return f"{self.name} (RWF{self.price})"


class Customer(models.Model):
    """
    A person who places orders.

    RELATIONSHIP: OneToOneField to auth.User.
    One user has exactly one customer profile (and vice versa).
    related_name="customer" means: from any user, request.user.customer
    gives you the profile. From any customer, customer.user gives the login.
    on_delete=CASCADE means deleting the user deletes the profile too.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer",
    )
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        full = self.user.get_full_name()
        return full or self.user.username


class Order(models.Model):
    """
    One customer order. May contain many menu items.

    RELATIONSHIP 1: ForeignKey to Customer.
    One customer, many orders. related_name="orders" means:
    customer.orders.all() gives every order that customer placed.

    RELATIONSHIP 2: ManyToManyField to MenuItem, THROUGH OrderItem.
    An order has many items; an item appears in many orders.
    We route through OrderItem (our own join model) so each link can
    store quantity and the price at the time of ordering. A plain
    ManyToManyField cannot store those extra columns.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    items = models.ManyToManyField(
        MenuItem,
        through="OrderItem",
        related_name="orders",
        blank=True,
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    # Cached total so list views don't re-aggregate every time.
    # Kept up to date by recalc_total() called after every save.
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer} - ${self.total_price}"

    def recalc_total(self, save=True):
        """
        SUM(quantity * unit_price) across all lines for this order.
        F() keeps the multiplication inside the database (one query, no loop).
        """
        aggregate = self.order_items.aggregate(
            total=Sum(F("quantity") * F("unit_price"))
        )
        self.total_price = aggregate["total"] or Decimal("0.00")
        if save:
            super().save(update_fields=["total_price"])
        return self.total_price


class OrderItem(models.Model):
    """
    The join model between Order and MenuItem (the "through" table).

    Each row = one line on a receipt: "2 x Skol Malt @ RWF 2,000".
    It carries:
      - order      FK to the parent order
      - menu_item  FK to the dish being ordered
      - quantity   how many
      - unit_price a SNAPSHOT of the price at order time, so that changing
                   the menu price later does not alter old receipts.

    Because Order.items uses through=OrderItem, you NEVER call
    order.items.add(dish). Instead you create an OrderItem row directly —
    that IS the many-to-many link, plus the extra data.
    """
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

    class Meta:
        unique_together = [("order", "menu_item")]

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price