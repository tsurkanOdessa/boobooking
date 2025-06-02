from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, viewsets, filters
from rest_framework.response import Response

from .models import RentHome, Attribute, Address
from .serializers import RentHomeSerializer, AttributeSerializer, AddressSerializer
from .permissions import IsOwner, IsOwnerOrManager, IsAdminOrManager

# Создание жилья (только для Owner)
class RentHomeCreateView(CreateAPIView):
    queryset = RentHome.objects.all()
    serializer_class = RentHomeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Фильтр по параметрам и аттрибутам
class RentHomeFilter(FilterSet):
    distance_to_sea = NumberFilter(field_name='distance_to_sea', lookup_expr='lte')
    distance_to_center = NumberFilter(field_name='distance_to_center', lookup_expr='lte')
    distance_to_transport = NumberFilter(field_name='distance_to_transport', lookup_expr='lte')
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')
    rooms = NumberFilter(field_name='rooms')
    beds = NumberFilter(field_name='beds')
    title = CharFilter(field_name='title', lookup_expr='icontains')
    attributes = CharFilter(method='filter_by_attributes')

    def filter_by_attributes(self, queryset, name, value):
        try:
            ids = list(map(int, value.split(',')))
        except ValueError:
            return queryset.none()
        return queryset.filter(attributes__in=ids).distinct()

    class Meta:
        model = RentHome
        fields = [
            'distance_to_sea',
            'distance_to_center',
            'distance_to_transport',
            'price_min', 'price_max',
            'rooms', 'beds',
            'title',
            'attributes',
        ]

class RentHomeViewSet(viewsets.ModelViewSet):
    queryset = RentHome.objects.all()
    serializer_class = RentHomeSerializer
    permission_classes = [IsOwnerOrManager]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = RentHomeFilter

    ordering_fields = ['price', 'distance_to_sea', 'distance_to_center', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'list' or self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:

            if  user.groups.exclude(name='Owner'):

                return RentHome.objects.all()

            return RentHome.objects.filter(owner=user)

        return RentHome.objects.filter(is_active=True)


    def perform_create(self, serializer):

        serializer.save(owner=self.request.user, is_active=False)

    def perform_update(self, serializer):
        instance = serializer.save()

        if instance.address:
            instance.is_active = True
        else:
            instance.is_active = False
        instance.save()


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminOrManager]
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Проверка уникальности имени
        if Attribute.objects.filter(name=serializer.validated_data['name']).exists():
            return Response(
                {"error": "Атрибут с таким именем уже существует."},
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            headers=headers
        )

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsOwnerOrManager]