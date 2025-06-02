from django.utils.translation import gettext_lazy as _
from django.db import models

class BookingStatus(models.TextChoices):
    PENDING = 'pending', _('Ожидает подтверждения')
    CONFIRMED = 'confirmed', _('Подтверждено')
    REJECTED = 'rejected', _('Отклонено')
    CANCELLED = 'cancelled', _('Отменено')
    COMPLETED = 'completed', _('Завершено')