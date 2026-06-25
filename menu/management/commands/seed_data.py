"""
Seed the database with realistic demo data.

Run:  python manage.py seed_data

Creating data through the ORM (not raw SQL) is deliberate: it exercises the
exact same relationship machinery the app uses at runtime, so if a link is
mis-declared this command fails loudly. It produces enough rows that the
list views, search, and daily report all have something to show in
screenshots.
"""

import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from menu.models import MenuCategory, MenuItem, Customer, Order, OrderItem


CATEGORIES = {
    "Starters": [
        ("Spring Rolls", "3500.00"), ("Garlic Bread", "2800.00"), ("Soup of the Day", "4000.00"),
    ],
    "Mains": [
        ("Margherita Pizza", "9500.00"), ("Grilled Chicken", "11000.00"),
        ("Beef Burger", "8750.00"), ("Veggie Pasta", "8000.00"),
    ],
    "Drinks": [
        ("Fresh Juice", "4500.00"), ("Skol", "2000.00"), ("Mutzig", "2000.00"),
    ],
    "Desserts": [
        ("Chocolate Cake", "4200.00"), ("Ice Cream", "3000.00"),
    ],
}


class Command(BaseCommand):
    help = "Populate the database with demo categories, items, customers and orders."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories and menu items...")
        items = []
        for cat_name, dishes in CATEGORIES.items():
            category, _ = MenuCategory.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"Our selection of {cat_name.lower()}."},
            )
            for dish_name, price in dishes:
                item, _ = MenuItem.objects.get_or_create(
                    category=category,
                    name=dish_name,
                    defaults={"price": Decimal(price), "description": f"Delicious {dish_name}."},
                )
                items.append(item)

        self.stdout.write("Seeding customers (with linked user accounts)...")
        customers = []
        for i in range(1, 6):
            username = f"customer{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": f"Customer{i}", "email": f"{username}@example.com"},
            )
            if created:
                user.set_password("demopass123")
                user.save()
            # The post_save signal already created the Customer profile.
            customer = user.customer
            customer.phone = f"+25078{i:07d}"
            customer.save()
            customers.append(customer)

        self.stdout.write("Seeding orders spread across the last few days...")
        for _ in range(15):
            customer = random.choice(customers)
            days_ago = random.randint(0, 4)
            created = timezone.now() - timezone.timedelta(days=days_ago)
            order = Order.objects.create(
                customer=customer,
                status=random.choice([Order.Status.PAID, Order.Status.PENDING]),
                created_at=created,
            )
            for item in random.sample(items, k=random.randint(1, 3)):
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=random.randint(1, 3),
                    unit_price=item.price,  # price snapshot
                )
            order.recalc_total()  # automatic total from the lines

        # An admin account for the admin-panel screenshots.
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "adminpass123")
            self.stdout.write("Created superuser 'admin' / 'adminpass123'.")

        self.stdout.write(self.style.SUCCESS("Done. Demo data is ready."))
