"""
Seed the database with realistic demo data.

Run:  python manage.py seed_data

Creates categories, menu items, tables, customers (with linked user accounts),
a staff user, and a spread of orders across the last few days.
"""

import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from menu.models import MenuCategory, MenuItem, Table, Customer, Order, OrderItem


CATEGORIES = {
    "Starters": [
        ("Spring Rolls", "3500.00", 10),
        ("Garlic Bread", "2800.00", 8),
        ("Soup of the Day", "4000.00", 15),
    ],
    "Mains": [
        ("Margherita Pizza", "9500.00", 20),
        ("Grilled Chicken", "11000.00", 25),
        ("Beef Burger", "8750.00", 18),
        ("Veggie Pasta", "8000.00", 20),
    ],
    "Drinks": [
        ("Fresh Juice", "4500.00", 5),
        ("Skol", "2000.00", 3),
        ("Mutzig", "2000.00", 3),
    ],
    "Desserts": [
        ("Chocolate Cake", "4200.00", 12),
        ("Ice Cream", "3000.00", 8),
    ],
}

TABLES = [
    (1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 8),
]


class Command(BaseCommand):
    help = "Populate the database with demo categories, items, tables, customers and orders."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories and menu items...")
        items = []
        for cat_name, dishes in CATEGORIES.items():
            category, _ = MenuCategory.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"Our selection of {cat_name.lower()}."},
            )
            for dish_name, price, prep_time in dishes:
                item, _ = MenuItem.objects.get_or_create(
                    category=category,
                    name=dish_name,
                    defaults={
                        "price": Decimal(price),
                        "description": f"Delicious {dish_name}.",
                        "preparation_time": prep_time,
                    },
                )
                items.append(item)

        self.stdout.write("Seeding tables...")
        tables = []
        for table_number, capacity in TABLES:
            table, _ = Table.objects.get_or_create(
                table_number=table_number,
                defaults={"capacity": capacity},
            )
            tables.append(table)

        self.stdout.write("Seeding customers (with linked user accounts)...")
        customers = []
        for i in range(1, 6):
            username = f"customer{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": f"Customer", "last_name": str(i), "email": f"{username}@example.com"},
            )
            if created:
                user.set_password("demopass123")
                user.save()
            customer = user.customer
            customer.phone = f"+25078{i:07d}"
            customer.role = Customer.CUSTOMER
            customer.save()
            customers.append(customer)

        self.stdout.write("Seeding staff account...")
        staff_user, created = User.objects.get_or_create(
            username="staff",
            defaults={"first_name": "Staff", "last_name": "Member", "email": "staff@example.com"},
        )
        if created:
            staff_user.set_password("staffpass123")
            staff_user.save()
        staff_user.customer.role = Customer.STAFF
        staff_user.customer.save()
        if created:
            self.stdout.write("  Created staff user 'staff' / 'staffpass123'.")

        self.stdout.write("Seeding orders spread across the last few days...")
        statuses = [
            Order.Status.PENDING,
            Order.Status.PREPARING,
            Order.Status.READY,
            Order.Status.SERVED,
            Order.Status.COMPLETED,
        ]
        for _ in range(15):
            customer = random.choice(customers)
            days_ago = random.randint(0, 4)
            created_at = timezone.now() - timezone.timedelta(days=days_ago)
            table = random.choice(tables + [None])
            order = Order.objects.create(
                customer=customer,
                customer_name=str(customer),
                table=table,
                status=random.choice(statuses),
                created_at=created_at,
            )
            for item in random.sample(items, k=random.randint(1, 3)):
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=random.randint(1, 3),
                    unit_price=item.price,
                )
            order.recalc_total()

        # Superuser for Django admin panel screenshots
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "adminpass123")
            # Mark admin's customer profile as staff too
            User.objects.get(username="admin").customer.role = Customer.STAFF
            User.objects.get(username="admin").customer.save()
            self.stdout.write("  Created superuser 'admin' / 'adminpass123'.")

        self.stdout.write(self.style.SUCCESS(
            "\nDone. Demo data ready.\n"
            "  Staff login  : staff / staffpass123\n"
            "  Customer login: customer1 / demopass123  (also customer2–5)\n"
            "  Admin panel  : admin / adminpass123"
        ))
