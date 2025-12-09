from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    registration_number = models.CharField(max_length=20, unique=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    
    # Organization
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.registration_number}"


class Driver(models.Model):
    # User
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='driver_profile')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    
    # Driver information
    license_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.license_number}"


class DeliverySession(models.Model):
    # Relations
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='sessions')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sessions')
    
    # Time
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Mileage
    start_mileage = models.PositiveIntegerField()
    end_mileage = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.vehicle} - {self.driver} ({self.start_time.strftime('%d/%m/%Y %H:%M')})"
