from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'', BookingViewSet)

booking_list = BookingViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
booking_detail = BookingViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
    'patch': 'partial_update',
})


urlpatterns = [
    path('', booking_list, name='booking-list'),
    path('<int:pk>/', booking_detail, name='booking-detail'),
]