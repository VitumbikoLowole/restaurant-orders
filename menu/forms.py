from django import forms
from django.forms import inlineformset_factory

from .models import MenuCategory, MenuItem, Customer, Order, OrderItem


class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field"}),
            "description": forms.Textarea(attrs={"class": "field", "rows": 3}),
        }


class MenuItemForm(forms.ModelForm):
    """
    The `category` field is a ForeignKey. ModelForm automatically renders
    it as a <select> dropdown populated with every MenuCategory row.
    You do not write the <option> tags — Django builds them from the DB.
    """
    class Meta:
        model = MenuItem
        fields = ["category", "name", "description", "price", "photo", "is_available"]
        widgets = {
            "category": forms.Select(attrs={"class": "field"}),
            "name": forms.TextInput(attrs={"class": "field"}),
            "description": forms.Textarea(attrs={"class": "field", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "field", "step": "0.01", "min": "0"}),
            "is_available": forms.CheckboxInput(),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["phone", "address"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "field"}),
            "address": forms.Textarea(attrs={"class": "field", "rows": 3}),
        }


class OrderForm(forms.ModelForm):
    """
    The order header. `customer` is a ForeignKey, so it renders as a dropdown.
    The line items (menu item + quantity) are handled by OrderItemFormSet below.
    """
    class Meta:
        model = Order
        fields = ["customer", "status"]
        widgets = {
            "customer": forms.Select(attrs={"class": "field"}),
            "status": forms.Select(attrs={"class": "field"}),
        }


class OrderItemForm(forms.ModelForm):
    """One line of an order: which menu item and how many."""
    class Meta:
        model = OrderItem
        fields = ["menu_item", "quantity"]
        widgets = {
            "menu_item": forms.Select(attrs={"class": "field line-item"}),
            "quantity": forms.NumberInput(
                attrs={"class": "field line-qty", "min": "1", "value": "1"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show items that are currently available to order.
        self.fields["menu_item"].queryset = MenuItem.objects.filter(
            is_available=True
        ).select_related("category")


# inlineformset_factory creates a set of OrderItemForms tied to one Order.
# extra=3 shows 3 blank lines. can_delete lets users remove lines.
# This is how you edit the "many" side of a relationship on the parent's page.
OrderItemFormSet = inlineformset_factory(
    parent_model=Order,
    model=OrderItem,
    form=OrderItemForm,
    extra=3,
    can_delete=True,
)


class MenuItemSearchForm(forms.Form):
    """
    Search/filter for the menu list. All fields optional.
    Drives the Q-object query in MenuItemListView.get_queryset().
    """
    q = forms.CharField(
        required=False,
        label="Keyword",
        widget=forms.TextInput(attrs={"class": "field", "placeholder": "Dish name..."}),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=MenuCategory.objects.all(),
        empty_label="All categories",
        widget=forms.Select(attrs={"class": "field"}),
    )
    min_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={"class": "field", "step": "0.01", "placeholder": "Min"}),
    )
    max_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={"class": "field", "step": "0.01", "placeholder": "Max"}),
    )
