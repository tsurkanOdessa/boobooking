from rest_framework import serializers
from django.utils import timezone
from .models.status import BookingStatus
from .models.booking import Booking

class BookingSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['status', 'cleanup_ready_datetime', 'renter']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        date_from = data['date_from']
        date_to = data['date_to']
        home = data['home']
        guests = data['guests']

        if date_from >= date_to:
            raise serializers.ValidationError("Дата начала должна быть раньше даты окончания.")

        if date_from < timezone.now().date():
            raise serializers.ValidationError("Дата начала не может быть в прошлом.")

        if (date_to - date_from).days < 1:
            raise serializers.ValidationError("Минимальный срок бронирования - 1 день.")

        if home.guests > 0 and guests > 0:
            if guests > home.guests:
                raise serializers.ValidationError("Слишком много гостей для этого жилья.")


        if not home.is_active and (not user or home.owner != user):
            raise serializers.ValidationError("Это жильё недоступно для бронирования.")

        temp_booking = Booking(
            home=home,
            date_from=date_from,
            date_to=date_to,
            status=BookingStatus.PENDING  # Используем PENDING для проверки
        )
        temp_booking.check_booking_conflicts()

        max_booking_days = getattr(home, 'max_booking_days', 365)
        if (date_to - date_from).days > max_booking_days:
            raise serializers.ValidationError(f"Максимальный срок бронирования - {max_booking_days} дней.")

        return data

    def create(self, validated_data):
        validated_data['renter'] = self.context['request'].user
        return super().create(validated_data)