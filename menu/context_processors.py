def user_role(request):
    """Inject user_is_staff into every template context."""
    user = request.user
    is_staff = False
    if user.is_authenticated:
        if user.is_staff or user.is_superuser:
            is_staff = True
        else:
            try:
                is_staff = user.customer.role == "staff"
            except Exception:
                pass
    return {"user_is_staff": is_staff}
