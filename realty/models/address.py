from django.db import models

class Address(models.Model):
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=20)

    class Meta:
        unique_together = ('country', 'city', 'street', 'house_number')

    def __str__(self):
        return f"{self.country}, {self.city}, {self.street} {self.house_number}"
