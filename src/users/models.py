from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    username = None

    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # accès admin

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email
    
    def get_role(self, organization):
        membership = self.memberships.filter(organization=organization).first()
        return membership.role if membership else None
    
    
class Membership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.email} in {self.organization.name} ({self.role})"