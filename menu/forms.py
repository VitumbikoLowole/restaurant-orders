from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.forms import inlineformset_factory

from .models import MenuCategory, MenuItem, Table, Customer, Order, OrderItem

User = get_user_model()


class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field"}),
            "description": forms.Textarea(attrs={"class": "field", "rows": 3}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            "category", "name", "description", "price",
            "preparation_time", "photo", "is_available",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "field"}),
            "name": forms.TextInput(attrs={"class": "field"}),
            "description": forms.Textarea(attrs={"class": "field", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "field", "step": "0.01", "min": "0"}),
            "preparation_time": forms.NumberInput(attrs={"class": "field", "min": "1"}),
            "is_available": forms.CheckboxInput(),
        }


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["table_number", "capacity", "table_status"]
        widgets = {
            "table_number": forms.NumberInput(attrs={"class": "field", "min": "1"}),
            "capacity": forms.NumberInput(attrs={"class": "field", "min": "1"}),
            "table_status": forms.Select(attrs={"class": "field"}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["phone", "address", "role"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "field"}),
            "address": forms.Textarea(attrs={"class": "field", "rows": 3}),
            "role": forms.Select(attrs={"class": "field"}),
        }


class CustomerProfileForm(forms.ModelForm):
    """Limited edit form for customers editing their own profile (no role field)."""
    class Meta:
        model = Customer
        fields = ["phone", "address"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "field"}),
            "address": forms.Textarea(attrs={"class": "field", "rows": 3}),
        }


class CustomerCreateForm(forms.Form):
    """Staff-only form: creates a new User + Customer profile in one step."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "field"}),
    )
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "field"}),
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "field"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "field"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "field"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": "field"}),
    )
    phone = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={"class": "field"}),
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "field", "rows": 3}),
    )
    role = forms.ChoiceField(
        choices=Customer.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "field"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            try:
                validate_password(p1)
            except forms.ValidationError as e:
                self.add_error("password1", e)
        return cleaned


class OrderForm(forms.ModelForm):
    def __init__(self, *args, is_staff=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff:
            # Customers don't choose the customer or table; those are set server-side.
            self.fields.pop("customer", None)
            self.fields.pop("table", None)
            # Customers can't manually advance order status
            self.fields.pop("status", None)

    class Meta:
        model = Order
        fields = ["customer", "table", "customer_name", "status", "special_instructions"]
        widgets = {
            "customer": forms.Select(attrs={"class": "field"}),
            "table": forms.Select(attrs={"class": "field"}),
            "customer_name": forms.TextInput(
                attrs={"class": "field", "placeholder": "Walk-in guest name (optional)"}
            ),
            "status": forms.Select(attrs={"class": "field"}),
            "special_instructions": forms.Textarea(attrs={"class": "field", "rows": 3}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["menu_item", "quantity", "special_requests"]
        widgets = {
            "menu_item": forms.Select(attrs={"class": "field line-item"}),
            "quantity": forms.NumberInput(
                attrs={"class": "field line-qty", "min": "1", "value": "1"}
            ),
            "special_requests": forms.Textarea(
                attrs={"class": "field", "rows": 2, "placeholder": "e.g. no onions"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_item"].queryset = MenuItem.objects.filter(
            is_available=True
        ).select_related("category")


OrderItemFormSet = inlineformset_factory(
    parent_model=Order,
    model=OrderItem,
    form=OrderItemForm,
    extra=3,
    can_delete=True,
)


class MenuItemSearchForm(forms.Form):
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
