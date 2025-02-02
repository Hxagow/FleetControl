from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class CheckoutSessionRecord(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text=_("The user who initiated the checkout.")
    )
    stripe_customer_id = models.CharField(max_length=255)
    stripe_checkout_session_id = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255)
    has_access = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)


class Subscription(models.Model):
    SUBSCRIPTION_TYPES = [
        ('standard_monthly', _('Standard Monthly')),
        ('standard_yearly', _('Standard Yearly')),
    ]

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('canceled', _('Canceled')),
        ('past_due', _('Past Due')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    subscription_type = models.CharField(max_length=50, choices=SUBSCRIPTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def __str__(self):
        return f"{self.user.email} - {self.subscription_type} ({self.status})"


