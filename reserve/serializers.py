from rest_framework import serializers
from .models.status import BookingStatus
from .models.booking import Booking

class BookingSerializer(serializers.ModelSerializer):
    price  = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['status', 'cleanup_ready_datetime', 'renter']

    def validate(self, data):
        date_from = data['date_from']
        date_to = data['date_to']
        home = data['home']
        guests = data['guests']

        if date_from >= date_to:
            raise serializers.ValidationError("Дата начала должна быть раньше даты окончания.")

        if guests > home.guests:
            raise serializers.ValidationError("Слишком много гостей для этого жилья.")

        temp_booking = Booking(
            home=home,
            date_from=date_from,
            date_to=date_to,
            status=BookingStatus.CONFIRMED
        )
        temp_booking.check_booking_conflicts()

        return data
