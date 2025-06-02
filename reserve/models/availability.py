from django.db import models
from realty.models.rent_home import RentHome

class Availability(models.Model):
    home = models.OneToOneField(RentHome, on_delete=models.CASCADE, related_name='availability')
    is_available = models.BooleanField(default=True)
    available_from = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.home.title} доступен с {self.available_from if self.available_from else 'сейчас'}"
