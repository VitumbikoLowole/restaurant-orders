# Reflection

The heart of this project was getting the relationships right, because every
feature ultimately leans on them. The one-to-one between Django's `User` and
my `Customer` let me keep authentication concerns separate from restaurant
profile data while still treating them as one person; the main challenge was
guaranteeing both rows are created together, which I solved by listening for
the `post_save` signal on `User` and creating the `Customer` profile there.
That way the link is forged whether the user is created through the registration
page, the admin panel, or the `createsuperuser` command — one rule, enforced
in one place.

The foreign keys were the most natural part — a category owning many items, a
customer owning many orders — and giving each one a clear `related_name` made
the reverse lookups (`category.items`, `customer.orders`) read almost like
plain English in the views and templates.

The hardest relationship was the order-to-menu-item many-to-many. A plain
`ManyToManyField` could not store quantity or price per link, so I introduced
an explicit `OrderItem` join model via `through=`. That unlocked two things I
initially underestimated: handling several order lines in one submission, which
required an inline formset bound to the parent order, and snapshotting the price
onto each line so historical totals do not change when the menu price moves.
Getting the formset to save in the right order — parent first to obtain a
primary key, then the child lines — took careful attention to how Django
resolves the FK during `save()`.

The other recurring challenge was query performance. Looping over orders and
rendering `order.customer.user.username` quietly fired a query per order. I
learned to apply `select_related` for forward single-valued foreign keys and
`prefetch_related` for the reverse, many-valued ones. Overall, designing the
data model carefully up front made the views, forms, serializers, and templates
fall into place naturally, since they all simply travel the relationships
defined once in `models.py`.
