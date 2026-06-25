from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_customer_profile(sender, instance, created, **kwargs):
    """
    Every time a User row is saved for the first time (created=True),
    immediately create the paired Customer profile.

    This is what makes the OneToOne link automatic. Whether the user
    is created through the registration page, the admin panel, or the
    createsuperuser command, this fires and creates the Customer row.
    Without this, you would have to remember to create the Customer
    manually in every code path that creates a user.
    """
    if created:
        Customer.objects.create(user=instance)