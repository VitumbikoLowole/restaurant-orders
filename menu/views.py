"""
Views for the menu app.

This is the layer that turns an HTTP request into a database operation and
a rendered page. Each view is annotated with the relationship work it does
and, where relevant, the SQL-shaping methods (select_related /
prefetch_related) used to keep list pages efficient.

Layout:
  * Home / dashboard
  * MenuCategory CRUD
  * MenuItem    CRUD  (+ Q-object search, photo upload)
  * Customer    CRUD
  * Order       CRUD  (+ formset-based placement, automatic totals)
  * Daily sales report
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import MenuCategory, MenuItem, Customer, Order, OrderItem
from .forms import (
    MenuCategoryForm, MenuItemForm, CustomerForm, OrderForm,
    OrderItemFormSet, MenuItemSearchForm,
)


# ==========================================================================
# Home
# ==========================================================================
def home(request):
    """
    Landing page with a few headline counts. Each count is one cheap
    aggregate query (SELECT COUNT(*)), so the dashboard stays light.
    """
    context = {
        "category_count": MenuCategory.objects.count(),
        "item_count": MenuItem.objects.count(),
        "customer_count": Customer.objects.count(),
        "order_count": Order.objects.count(),
    }
    return render(request, "menu/home.html", context)


# ==========================================================================
# MenuCategory CRUD
# ==========================================================================
class CategoryListView(ListView):
    model = MenuCategory
    template_name = "menu/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        # annotate() adds a COUNT of related items per category in ONE query
        # (a LEFT JOIN + GROUP BY), instead of N extra COUNT queries in the
        # template. This is the relationship being aggregated at the DB level.
        return MenuCategory.objects.annotate(num_items=Count("items"))


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = MenuCategory
    form_class = MenuCategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        messages.success(self.request, "Category created.")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuCategory
    form_class = MenuCategoryForm
    template_name = "menu/category_form.html"
    success_url = reverse_lazy("category_list")


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuCategory
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("category_list")

    def post(self, request, *args, **kwargs):
        # MenuItem.category uses on_delete=PROTECT, so deleting a category
        # that still has items raises ProtectedError. We catch it and turn
        # it into a friendly message instead of a 500 page.
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
# MenuItem CRUD  (+ search)
# ==========================================================================
class MenuItemListView(ListView):
    model = MenuItem
    template_name = "menu/menuitem_list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        """
        Two jobs here:

        1) select_related("category"): MenuItem.category is a ForeignKey
           (many items -> one category). Without select_related, rendering
           `item.category.name` for every row fires one extra query per row
           (the classic N+1 problem). select_related turns it into a single
           SQL JOIN, so the whole page is one query for items+categories.

        2) Search via Q objects. We build a Q() expression from whatever
           filter fields were submitted and AND them together. Each branch
           is an independent, optional criterion -- this is the brief's
           "at least 2 filter criteria using Q objects":
              - keyword matches name OR description  (Q | Q)
              - category exact match
              - price >= min_price
              - price <= max_price
        """
        qs = MenuItem.objects.select_related("category")

        self.search_form = MenuItemSearchForm(self.request.GET or None)
        if self.search_form.is_valid():
            cd = self.search_form.cleaned_data

            keyword = cd.get("q")
            if keyword:
                # OR across two columns inside a single Q expression.
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
        # Preserve the querystring across pagination links.
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


class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/menuitem_form.html"
    success_url = reverse_lazy("menuitem_list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item created.")
        return super().form_valid(form)


class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = "menu/menuitem_form.html"
    success_url = reverse_lazy("menuitem_list")


class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("menuitem_list")


# ==========================================================================
# Customer CRUD
# ==========================================================================
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "menu/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):
        # Customer.user is a OneToOne (a FK under the hood), so the same
        # N+1 logic applies: select_related("user") joins the auth_user row
        # in once. annotate() also counts each customer's orders in-query.
        return (
            Customer.objects.select_related("user")
            .annotate(num_orders=Count("orders"))
        )


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "menu/customer_form.html"
    success_url = reverse_lazy("customer_list")


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("customer_list")


# ==========================================================================
# Order CRUD  (+ placement with line items and automatic total)
# ==========================================================================
def _price_map():
    """
    Build {menu_item_id: "price"} for every available item.

    The order form's JavaScript reads this map to compute line totals and a
    running total live, before the form is even submitted. It is only a
    convenience preview -- the authoritative total is still recomputed on
    the server from the saved OrderItem rows.
    """
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
        """
        Orders touch three related tables, so we combine both optimisation
        tools:
          * select_related("customer", "customer__user"): follow the
            many-to-one FK chain Order -> Customer -> User in the same JOIN.
          * prefetch_related("order_items__menu_item"): the order lines are
            a reverse FK / many side, which select_related cannot do in one
            row. prefetch_related runs a second query that loads ALL lines
            for ALL listed orders at once and stitches them in Python,
            turning a potential N+1 into exactly 2 queries total.
        """
        return (
            Order.objects.select_related("customer", "customer__user")
            .prefetch_related("order_items__menu_item")
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "menu/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related(
            "customer", "customer__user"
        ).prefetch_related("order_items__menu_item")


@login_required
def order_create(request):
    """
    Place an order: choose a customer + status (OrderForm) and add one or
    more lines (OrderItemFormSet). This is where the many-to-many through
    OrderItem is actually written, and where the total is computed.

    Flow:
      1. Bind both the parent form and the inline formset to POST data
         (and request.FILES is unused here; no uploads on this form).
      2. Validate both. If valid, save inside a single DB transaction so a
         half-written order can never be committed.
      3. For each line, snapshot the chosen item's current price into
         unit_price (so historical totals are stable), then save the line.
      4. Call order.recalc_total() -> the SUM(quantity*unit_price) query
         that fills total_price automatically.
    """
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save()
                # Bind the formset's children to the freshly-created order.
                formset.instance = order
                lines = formset.save(commit=False)
                for line in lines:
                    # Price snapshot taken from the selected MenuItem.
                    line.unit_price = line.menu_item.price
                    line.save()
                # Honour any rows the user marked for deletion.
                for obj in formset.deleted_objects:
                    obj.delete()
                order.recalc_total()  # automatic total
            messages.success(
                request, f"Order #{order.pk} placed. Total RWF{order.total_price}."
            )
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(
        request,
        "menu/order_form.html",
        {
            "form": form,
            "formset": formset,
            "is_create": True,
            "price_map_json": _price_map(),
        },
    )


@login_required
def order_update(request, pk):
    """Edit an existing order's header and lines, then recompute its total."""
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save()
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
        form = OrderForm(instance=order)
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
        },
    )


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = "menu/confirm_delete.html"
    success_url = reverse_lazy("order_list")


# ==========================================================================
# Daily sales report
# ==========================================================================
@login_required
def daily_sales_report(request):
    """
    "Total per day" report.

    We group every PAID/PENDING order by its calendar date and sum the
    cached total_price column. TruncDate collapses the timestamp to a date
    so GROUP BY buckets by day:

        SELECT DATE(created_at) AS day,
               COUNT(*)          AS num_orders,
               SUM(total_price)  AS revenue
        FROM menu_order
        GROUP BY DATE(created_at)
        ORDER BY day DESC;

    The result is a queryset of dict-like rows the template renders as a
    table. We also compute today's revenue separately for the headline.
    """
    rows = (
        Order.objects.exclude(status=Order.Status.CANCELLED)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(num_orders=Count("id"), revenue=Sum("total_price"))
        .order_by("-day")
    )

    today = timezone.localdate()
    today_revenue = (
        Order.objects.filter(created_at__date=today)
        .exclude(status=Order.Status.CANCELLED)
        .aggregate(total=Sum("total_price"))["total"]
        or Decimal("0.00")
    )

    return render(
        request,
        "menu/daily_report.html",
        {"rows": rows, "today": today, "today_revenue": today_revenue},
    )
