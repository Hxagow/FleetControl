from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_countries.fields import CountryField
import uuid
from datetime import timedelta
from django.utils import timezone
from src.users.models import OrganizationUser


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = CountryField(blank=True, null=True)

    logo = models.ImageField(upload_to='logos', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    language = models.CharField(
        max_length=5,
        choices=[
            ('fr', _('French')),
            ('en', _('English')),
            ('de', _('German')),
        ],
        default='fr'
    )

    # Stripe
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, blank=True, null=True)
    subscription_start = models.DateTimeField(blank=True, null=True)
    subscription_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('accepted', _('Acceptée')),
        ('declined', _('Refusée')),
        ('expired', _('Expirée')),
    ]

    email = models.EmailField(_('Email'))
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_invitations')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    role = models.CharField(max_length=10, choices=OrganizationUser.ROLE_CHOICES, default='member',)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('email', 'organization')
        verbose_name = _('Invitation')
        verbose_name_plural = _('Invitations')

    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)  # Expire dans 7 jours
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def can_be_accepted(self):
        return self.status == 'pending' and not self.is_expired()