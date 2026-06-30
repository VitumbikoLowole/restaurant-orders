from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0001_initial"),
    ]

    operations = [
        # Add role field to Customer
        migrations.AddField(
            model_name="customer",
            name="role",
            field=models.CharField(
                choices=[("staff", "Staff"), ("customer", "Customer")],
                default="customer",
                max_length=10,
            ),
        ),
        # Create Table model
        migrations.CreateModel(
            name="Table",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("table_number", models.PositiveIntegerField(unique=True)),
                ("capacity", models.PositiveIntegerField()),
                (
                    "table_status",
                    models.CharField(
                        choices=[
                            ("available", "Available"),
                            ("occupied", "Occupied"),
                            ("reserved", "Reserved"),
                        ],
                        default="available",
                        max_length=10,
                    ),
                ),
            ],
            options={"ordering": ["table_number"]},
        ),
        # Add preparation_time to MenuItem
        migrations.AddField(
            model_name="menuitem",
            name="preparation_time",
            field=models.PositiveIntegerField(
                default=15,
                help_text="Estimated preparation time in minutes",
            ),
        ),
        # Make Order.customer nullable (walk-in orders may have no account)
        migrations.AlterField(
            model_name="order",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="menu.customer",
            ),
        ),
        # Add table FK to Order
        migrations.AddField(
            model_name="order",
            name="table",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="menu.table",
            ),
        ),
        # Add customer_name to Order
        migrations.AddField(
            model_name="order",
            name="customer_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        # Add special_instructions to Order
        migrations.AddField(
            model_name="order",
            name="special_instructions",
            field=models.TextField(blank=True),
        ),
        # Update Order.status choices (Pending → Preparing → Ready → Served → Completed)
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("preparing", "Preparing"),
                    ("ready", "Ready"),
                    ("served", "Served"),
                    ("completed", "Completed"),
                ],
                default="pending",
                max_length=10,
            ),
        ),
        # Add special_requests to OrderItem
        migrations.AddField(
            model_name="orderitem",
            name="special_requests",
            field=models.TextField(blank=True),
        ),
    ]
