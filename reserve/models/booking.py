from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from realty.models.rent_home import RentHome
from reserve.models.status import BookingStatus
from rest_framework import serializers

class Booking(models.Model):
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    home = models.ForeignKey(RentHome, on_delete=models.CASCADE, related_name='bookings')
    date_from = models.DateField()
    date_to = models.DateField()
    guests = models.PositiveIntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(99)],
    help_text="Количество гостей (1-99)"
    )
    price = models.PositiveIntegerField(verbose_name="Цена", help_text="Общая стоимость бронирования в выбранный период", null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    cleanup_ready_datetime = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def check_booking_conflicts(self):
        overlapping = Booking.objects.filter(
            home=self.home,
            status=BookingStatus.CONFIRMED,
            date_from__lt=self.date_to,
            date_to__gt=self.date_from
        ).exclude(id=self.id).exists()

        if overlapping:
            raise serializers.ValidationError("Жильё занято на выбранные даты.")

        if Booking.objects.filter(
                home=self.home,
                date_from=self.date_from,
                date_to=self.date_to,
                status=BookingStatus.CONFIRMED
        ).exclude(id=self.id).exists():
            raise serializers.ValidationError("Такое подтвержденное бронирование уже существует.")


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.renter} → {self.home} ({self.date_from} - {self.date_to})"
