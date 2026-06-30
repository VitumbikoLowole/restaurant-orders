"""
Views for the menu app.

Role model:
  - Staff  : is_staff / is_superuser on auth.User  OR  customer.role == 'staff'
  - Customer: everyone else (authenticated regular users)

Access rules:
  MenuCategory  : List = all;  Create/Update/Delete = Staff only
  MenuItem      : List/Detail = all;  Create/Update/Delete = Staff only
  Table         : All CRUD = Staff only
  Customer      : List/Create/Delete = Staff only;  Update = staff OR own profile
  Order         : List/Detail/Create = authenticated;
                  customers see only their own orders;
                  Update/Delete = Staff only
  Reports       : Staff only
"""

from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import MenuCategory, MenuItem, Table, Customer, Order, OrderItem
from .forms import (
    MenuCategoryForm, MenuItemForm, TableForm,
    CustomerForm, CustomerProfileForm, CustomerCreateForm,
    OrderForm, OrderItemFormSet, MenuItemSearchForm,
)

User = get_user_model()


# ==========================================================================
# Role helpers
# ==========================================================================

def is_staff_member(user):
    """True when the user holds Staff privileges."""
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    try:
        return user.customer.role == Customer.STAFF
    except Customer.DoesNotExist:
        return False


class StaffRequiredMixin(LoginRequiredMixin):
    """CBV mixin: restrict view to Staff role."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not is_staff_member(request.user):
            messages.error(request, "Staff access required.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


def staff_required(view_func):
    """FBV decorator: restrict view to Staff role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as django_settings
            return redirect(f"{django_settings.LOGIN_URL}?next={request.path}")
        if not is_staff_member(request.user):
            messages.error(request, "Staff access required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================================================
# Home / dashboard
# ==========================================================================

def home(request):
    if not request.user.is_authenticated:
        return render(request, "menu/home.html", {})

    if is_staff_member(request.user):
        context = {
            "category_count": MenuCategory.objects.count(),
            "item_count": MenuItem.objects.count(),
            "table_count": Table.objects.count(),
            "customer_count": Customer.objects.count(),
            "order_count": Order.objects.count(),
            "pending_count": Order.objects.filter(status=Order.Status.PENDING).count(),
        }
    else:
        try:
            my_orders = Order.objects.filter(customer=request.user.customer)
        except Customer.DoesNotExist:
            my_orders = Order.objects.none()
        context = {
            "item_count": MenuItem.objects.filter(is_available=True).count(),
            "my_order_count": my_orders.count(),
            "my_pending_count": my_orders.filter(status=Order.Status.PENDING).count(),
        }
    return render(request, "menu/home.html", context)


# ==========================================================================
# MenuCategory CRUD  (Staff only for CUD)
# ==========================================================================

class CategoryListView(ListView):
    model = MenuCategory
    template_name = "menu/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return MenuCategory.objects.annotate(num_items=Count("items"))


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = MenuCategory
    form_class = MenuCategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        messages.success(self.request, "Category created.")
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = MenuCategory
    form_class = MenuCategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        messages.success(self.request, "Category updated.")
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = MenuCategory
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("category_list")

    def post(self, request, *args, **kwargs):
        from django.db.models import ProtectedError
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete a category that still has menu items. "
                "Move or delete those items first.",
            )
            return redirect("category_list")
        messages.success(request, "Category deleted.")
        return redirect("category_list")


# ==========================================================================
# MenuItem CRUD  (List/Detail = all; CUD = Staff only)
# ==========================================================================

class MenuItemListView(ListView):
    model = MenuItem
    template_name = "menu/menuitem_list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        qs = MenuItem.objects.select_related("category")
        self.search_form = MenuItemSearchForm(self.request.GET or None)
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data
            keyword = cd.get("q")
            if keyword:
                qs = qs.filter(
                    Q(name__icontains=keyword) | Q(description__icontains=keyword)
                )
            category = cd.get("category")
            if category:
                qs = qs.filter(Q(category=category))
            min_price = cd.get("min_price")
            if min_price is not None:
                qs = qs.filter(Q(price__gte=min_price))
            max_price = cd.get("max_price")
            if max_price is not None:
                qs = qs.filter(Q(price__lte=max_price))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_form"] = self.search_form
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring"] = params.urlencode()
        return ctx


class MenuItemDetailView(DetailView):
    model = MenuItem
    template_name = "menu/menuitem_detail.html"
    context_object_name = "item"

    def get_queryset(self):
        return MenuItem.objects.select_related("category")


class MenuItemCreateView(StaffRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/menuitem_form.html"
    success_url = reverse_lazy("menuitem_list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item created.")
        return super().form_valid(form)


class MenuItemUpdateView(StaffRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/menuitem_form.html"
    success_url = reverse_lazy("menuitem_list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item updated.")
        return super().form_valid(form)


class MenuItemDeleteView(StaffRequiredMixin, DeleteView):
    model = MenuItem
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("menuitem_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Menu item deleted.")
        return super().post(request, *args, **kwargs)


# ==========================================================================
# Table CRUD  (Staff only)
# ==========================================================================

class TableListView(StaffRequiredMixin, ListView):
    model = Table
    template_name = "menu/table_list.html"
    context_object_name = "tables"

    def get_queryset(self):
        return Table.objects.annotate(num_orders=Count("orders"))


class TableCreateView(StaffRequiredMixin, CreateView):
    model = Table
    form_class = TableForm
    template_name = "menu/table_form.html"
    success_url = reverse_lazy("table_list")

    def form_valid(self, form):
        messages.success(self.request, f"Table {form.instance.table_number} added.")
        return super().form_valid(form)


class TableUpdateView(StaffRequiredMixin, UpdateView):
    model = Table
    form_class = TableForm
    template_name = "menu/table_form.html"
    success_url = reverse_lazy("table_list")

    def form_valid(self, form):
        messages.success(self.request, f"Table {form.instance.table_number} updated.")
        return super().form_valid(form)


class TableDeleteView(StaffRequiredMixin, DeleteView):
    model = Table
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("table_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Table deleted.")
        return super().post(request, *args, **kwargs)


# ==========================================================================
# Customer CRUD
#   List/Create/Delete = Staff only
#   Update = Staff OR own profile
# ==========================================================================

class CustomerListView(StaffRequiredMixin, ListView):
    model = Customer
    template_name = "menu/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):
        return (
            Customer.objects.select_related("user")
            .annotate(num_orders=Count("orders"))
        )


class CustomerCreateView(StaffRequiredMixin, View):
    template_name = "menu/customer_create_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": CustomerCreateForm()})

    def post(self, request):
        form = CustomerCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                username=cd["username"],
                first_name=cd.get("first_name", ""),
                last_name=cd.get("last_name", ""),
                email=cd.get("email", ""),
                password=cd["password1"],
            )
            # Signal already created the Customer; update extra fields.
            customer = user.customer
            customer.phone = cd.get("phone", "")
            customer.address = cd.get("address", "")
            customer.role = cd["role"]
            customer.save()
            messages.success(request, f"Account created for {user.username}.")
            return redirect("customer_list")
        return render(request, self.template_name, {"form": form})


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = "menu/customer_form.html"
    success_url = reverse_lazy("customer_list")

    def get_form_class(self):
        # Staff can change role; customers editing themselves cannot.
        if is_staff_member(self.request.user):
            return CustomerForm
        return CustomerProfileForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        if not is_staff_member(request.user) and obj.user != request.user:
            messages.error(request, "You can only edit your own profile.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if is_staff_member(self.request.user):
            return reverse_lazy("customer_list")
        return reverse_lazy("home")

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)


class CustomerDeleteView(StaffRequiredMixin, DeleteView):
    model = Customer
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("customer_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Customer deleted.")
        return super().post(request, *args, **kwargs)


# ==========================================================================
# Order CRUD
#   List/Detail/Create = authenticated (customers see own orders only)
#   Update/Delete = Staff only
# ==========================================================================

def _price_map():
    return {
        str(pk): str(price)
        for pk, price in MenuItem.objects.filter(is_available=True).values_list(
            "id", "price"
        )
    }


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "menu/order_list.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        qs = (
            Order.objects.select_related("customer", "customer__user", "table")
            .prefetch_related("order_items__menu_item")
        )
        if not is_staff_member(self.request.user):
            try:
                qs = qs.filter(customer=self.request.user.customer)
            except Customer.DoesNotExist:
                qs = qs.none()
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "menu/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        qs = Order.objects.select_related(
            "customer", "customer__user", "table"
        ).prefetch_related("order_items__menu_item")
        if not is_staff_member(self.request.user):
            try:
                qs = qs.filter(customer=self.request.user.customer)
            except Customer.DoesNotExist:
                qs = qs.none()
        return qs


@login_required
def order_create(request):
    user_is_staff = is_staff_member(request.user)

    if request.method == "POST":
        form = OrderForm(request.POST, is_staff=user_is_staff)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if not user_is_staff:
                    try:
                        order.customer = request.user.customer
                        if not order.customer_name:
                            order.customer_name = str(request.user.customer)
                    except Customer.DoesNotExist:
                        pass
                # Auto-fill customer_name from linked customer if blank
                if order.customer and not order.customer_name:
                    order.customer_name = str(order.customer)
                order.save()
                formset.instance = order
                lines = formset.save(commit=False)
                for line in lines:
                    line.unit_price = line.menu_item.price
                    line.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                order.recalc_total()
            messages.success(
                request, f"Order #{order.pk} placed. Total RWF{order.total_price}."
            )
            return redirect("order_detail", pk=order.pk)
    else:
        initial = {}
        if not user_is_staff:
            try:
                initial["customer_name"] = str(request.user.customer)
            except Customer.DoesNotExist:
                pass
        form = OrderForm(is_staff=user_is_staff, initial=initial)
        formset = OrderItemFormSet()

    return render(
        request,
        "menu/order_form.html",
        {
            "form": form,
            "formset": formset,
            "is_create": True,
            "price_map_json": _price_map(),
            "user_is_staff": user_is_staff,
        },
    )


@staff_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order, is_staff=True)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if order.customer and not order.customer_name:
                    order.customer_name = str(order.customer)
                order.save()
                lines = formset.save(commit=False)
                for line in lines:
                    if line.unit_price is None:
                        line.unit_price = line.menu_item.price
                    line.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                order.recalc_total()
            messages.success(request, f"Order #{order.pk} updated.")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm(instance=order, is_staff=True)
        formset = OrderItemFormSet(instance=order)

    return render(
        request,
        "menu/order_form.html",
        {
            "form": form,
            "formset": formset,
            "order": order,
            "is_create": False,
            "price_map_json": _price_map(),
            "user_is_staff": True,
        },
    )


class OrderDeleteView(StaffRequiredMixin, DeleteView):
    model = Order
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("order_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Order deleted.")
        return super().post(request, *args, **kwargs)


# ==========================================================================
# Daily sales report  (Staff only)
# ==========================================================================

@staff_required
def daily_sales_report(request):
    rows = (
        Order.objects.exclude(status=Order.Status.COMPLETED)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(num_orders=Count("id"), revenue=Sum("total_price"))
        .order_by("-day")
    )

    today = timezone.localdate()
    today_revenue = (
        Order.objects.filter(created_at__date=today)
        .exclude(status=Order.Status.COMPLETED)
        .aggregate(total=Sum("total_price"))["total"]
        or Decimal("0.00")
    )

    return render(
        request,
        "menu/daily_report.html",
        {"rows": rows, "today": today, "today_revenue": today_revenue},
    )
