from django.contrib import admin
from . import models

@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'status', 'current_period_end')
    list_filter = ('subscription_type', 'status')
    search_fields = ('user__email', 'stripe_subscription_id')
    ordering = ('-created_at',)

@admin.register(models.CheckoutSessionRecord)
class CheckoutSessionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_access', 'is_completed')
    list_filter = ('has_access', 'is_completed')
    search_fields = ('user__email', 'stripe_customer_id')
