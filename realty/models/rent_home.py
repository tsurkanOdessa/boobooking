from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from .attributes import Attribute
from .address import Address

class RentHome(models.Model):
    TYPE_CHOICES = (
        ('Hause', 'Hause'),
        ('Villa', 'Villa'),
        ('Apartment', 'Apartment'),
        ('Other', 'Other'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rent_homes'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='Apartment'
    )
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    rooms = models.PositiveIntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(99)],
    help_text="Количество комнат (1-99)"
    )
    beds = models.PositiveIntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(99)],
    help_text="Количество спальных мест (1-99)"
    )
    guests = models.PositiveIntegerField(
    default=0,
    validators=[MinValueValidator(0), MaxValueValidator(99)],
    help_text="Количество гостей (1-99)"
    )
    area = models.FloatField(help_text="Площадь в квадратных метрах")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    # Дополнительные параметры
    distance_to_sea = models.FloatField(null=True, blank=True, help_text="в км")
    distance_to_center = models.FloatField(null=True, blank=True, help_text="в км")
    distance_to_transport = models.FloatField(null=True, blank=True, help_text="в км")

    attributes = models.ManyToManyField(Attribute, blank=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.address and not self.is_active:
            self.is_active = True
        super().save(*args, **kwargs)