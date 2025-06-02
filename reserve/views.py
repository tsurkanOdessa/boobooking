from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from django.utils import timezone

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
            return Response({"error": "Требуется аутентификация"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_superuser or user.role in ['Admin', 'Manager']:
            return Booking.objects.all()

        queryset = Booking.objects.exclude(status=BookingStatus.CANCELLED)

        if user.role == 'Owner':

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
            return Response({"error": "Превышено максимальное количество гостей."},
                            status=status.HTTP_400_BAD_REQUEST)


        if home.owner == request.user:
            price = 0


        temp_booking = Booking(
            home=home,
            date_from=date_from,
            date_to=date_to,
            status=BookingStatus.CONFIRMED
        )
        try:
            temp_booking.check_booking_conflicts()
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        days = (date_to - date_from).days
        price = days * home.price


        if 'price' in request.data and home.owner == request.user:
            price = request.data['price']

        serializer.save(
            renter=request.user,
            status=BookingStatus.PENDING,
            price=price
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        booking = self.get_object()
        user = request.user

        if not (user == booking.home.owner or user.is_superuser or user.role in ['Admin', 'Manager']):
            return Response({"error": "Доступ запрещен"}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get("action")
        new_status = request.data.get("status")
        cleaning_ready_at = request.data.get("cleaning_ready_at")

        if action:
            if booking.status == BookingStatus.COMPLETED and not user.is_superuser:
                return Response({"error": "Невозможно изменить завершенные бронирования"},
                                status=status.HTTP_400_BAD_REQUEST)

            if action == "approve":
                Booking.objects.filter(
                    home=booking.home,
                    date_from__lt=booking.date_to,
                    date_to__gt=booking.date_from,
                    status=BookingStatus.PENDING
                ).exclude(id=booking.id).update(status=BookingStatus.REJECTED)

                booking.status = BookingStatus.CONFIRMED
            elif action == "reject":
                booking.status = BookingStatus.REJECTED
            else:
                return Response({"error": "Действие не определено"},
                                status=status.HTTP_400_BAD_REQUEST)

            if cleaning_ready_at:
                booking.cleanup_ready_datetime = cleaning_ready_at

            booking.save()
        elif new_status:

            if user.role not in ['Admin', 'Manager']:
                return Response({"error": "Прямое изменение статуса не допускается."},
                                status=status.HTTP_403_FORBIDDEN)

            valid_statuses = [s.value for s in BookingStatus]
            if new_status not in valid_statuses:
                return Response({"error": "Неверный статус"},
                                status=status.HTTP_400_BAD_REQUEST)

            booking.status = new_status
            booking.save()
        else:
            return Response({"error": "Действие или статус не указаны"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(BookingSerializer(booking).data)

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()

        if not (request.user == booking.home.owner or request.user.is_superuser):
            return Response({"error": "Доступ запрещен"},
                            status=status.HTTP_403_FORBIDDEN)

        booking.status = BookingStatus.CANCELLED
        booking.save()

        return Response(status=status.HTTP_204_NO_CONTENT)