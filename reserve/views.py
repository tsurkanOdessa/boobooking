from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from realty.permissions import IsAdminOrManager
from .models.booking import Booking
from .models.status import BookingStatus
from .serializers import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Response({"error": "Необходимо зарегистрироваться."}, status=400)

        if user.is_superuser or user.role in ['Admin', 'Manager']:
            queryset = Booking.objects.all()
        else:
            queryset = Booking.objects.exclude(status=BookingStatus.CANCELLED)

        #queryset = Booking.objects.filter(~Q(status=BookingStatus.CANCELLED))

        if user.is_superuser or user.role in ['Admin', 'Manager']:
            return queryset
        elif user.role == 'Owner':
            return queryset.filter(home__owner=user)
        elif user.role == 'Renter':
            return queryset.filter(renter=user)
        return Booking.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        home = serializer.validated_data['home']
        date_from = serializer.validated_data['date_from']
        date_to = serializer.validated_data['date_to']
        guests = serializer.validated_data['guests']

        if home.guests != 0 and guests > home.guests:
            return Response({"error": "Превышено максимальное количество гостей."}, status=400)

        temp_booking = Booking(
            home=home,
            date_from=date_from,
            date_to=date_to,
            status=BookingStatus.CONFIRMED
        )
        try:
            temp_booking.check_booking_conflicts()
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=400)

        days = (date_to - date_from).days
        price = days * home.price

        serializer.save(renter=request.user, status=BookingStatus.PENDING, price=price)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        booking = self.get_object()
        user = request.user

        if user != booking.home.owner:
            return Response({"error": "Только владелец жилья может изменять статус бронирования."}, status=403)

        action = request.data.get("action")
        new_status = request.data.get("status")
        cleaning_ready_at = request.data.get("cleaning_ready_at")

        if action:
            if booking.status == BookingStatus.COMPLETED:
                return Response({"error": "Нельзя изменять завершённые бронирования."}, status=400)

            if action == "approve":
                # Отменяем другие PENDING бронирования с конфликтующими датами по этому дому
                Booking.objects.filter(
                    home=booking.home,
                    date_from__lt=booking.date_to,
                    date_to__gt=booking.date_from,
                    status=BookingStatus.PENDING
                ).exclude(id=booking.id).update(status=BookingStatus.REJECTED)

                booking.status = BookingStatus.CONFIRMED
                if cleaning_ready_at:
                    booking.cleanup_ready_datetime = cleaning_ready_at

                try:
                    booking.check_booking_conflicts()
                except serializers.ValidationError as e:
                    return Response({"error": e.detail}, status=400)

                booking.save()

            elif action == "reject":
                booking.status = BookingStatus.REJECTED
                if cleaning_ready_at:
                    booking.cleanup_ready_datetime = cleaning_ready_at
                booking.save()
            else:
                return Response({"error": "Неверное значение для action. Допустимы только 'approve' или 'reject'."},
                                status=400)

        # Если есть только status — разрешаем менять, кроме завершённых
        elif new_status:
            if booking.status == BookingStatus.COMPLETED:
                return Response({"error": "Нельзя изменять статус завершённого бронирования."}, status=400)

            valid_statuses = {
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                BookingStatus.REJECTED,
                BookingStatus.CANCELLED,
                BookingStatus.COMPLETED,
            }

            if new_status.lower() not in valid_statuses:
                return Response({"error": "Недопустимый статус."}, status=400)

            booking.status = new_status.lower()
            if cleaning_ready_at:
                booking.cleanup_ready_datetime = cleaning_ready_at
            booking.save()

        else:
            return Response({"error": "Необходимо указать 'action' или 'status'."}, status=400)

        return Response(BookingSerializer(booking).data)

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()

        if request.user != booking.home.owner and not request.user.is_superuser:
            return Response({"error": "Нет прав на удаление."}, status=status.HTTP_403_FORBIDDEN)

        booking.status = BookingStatus.CANCELLED
        booking.save()

        return Response(status=status.HTTP_204_NO_CONTENT)