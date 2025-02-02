from django.contrib import admin
from django.urls import path, include
from subscriptions import views

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('cancel/', views.cancel, name='cancel'),
    path('success/', views.success, name='success'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('direct-to-customer-portal/', views.direct_to_customer_portal, name='direct-to-customer-portal'),
    path('collect-stripe-webhook/', views.collect_stripe_webhook, name='collect-stripe-webhook'),
]
