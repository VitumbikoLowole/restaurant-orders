from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # MenuCategory CRUD
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # MenuItem CRUD (search lives on the list view)
    path("menu/", views.MenuItemListView.as_view(), name="menuitem_list"),
    path("menu/new/", views.MenuItemCreateView.as_view(), name="menuitem_create"),
    path("menu/<int:pk>/", views.MenuItemDetailView.as_view(), name="menuitem_detail"),
    path("menu/<int:pk>/edit/", views.MenuItemUpdateView.as_view(), name="menuitem_update"),
    path("menu/<int:pk>/delete/", views.MenuItemDeleteView.as_view(), name="menuitem_delete"),

    # Table CRUD (Staff only)
    path("tables/", views.TableListView.as_view(), name="table_list"),
    path("tables/new/", views.TableCreateView.as_view(), name="table_create"),
    path("tables/<int:pk>/edit/", views.TableUpdateView.as_view(), name="table_update"),
    path("tables/<int:pk>/delete/", views.TableDeleteView.as_view(), name="table_delete"),

    # Customer CRUD
    path("customers/", views.CustomerListView.as_view(), name="customer_list"),
    path("customers/new/", views.CustomerCreateView.as_view(), name="customer_create"),
    path("customers/<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="customer_update"),
    path("customers/<int:pk>/delete/", views.CustomerDeleteView.as_view(), name="customer_delete"),

    # Order CRUD
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/new/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/edit/", views.order_update, name="order_update"),
    path("orders/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),

    # Reports (Staff only)
    path("reports/daily/", views.daily_sales_report, name="daily_report"),
]
