from django.urls import path
from .views import RentHomeViewSet, AddressViewSet, AttributeViewSet

rent_home_list = RentHomeViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
rent_home_detail = RentHomeViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

addresses_list = AddressViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

addresses_detail = AddressViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

attributes_list = AttributeViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

attributes_detail = AttributeViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
})

urlpatterns = [
    path('', rent_home_list, name='realty-list'),
    path('<int:pk>/', rent_home_detail, name='realty-detail'),

    path('addresses/', addresses_list, name='address-list'),
    path('addresses/<int:pk>/', addresses_detail, name='address-detail'),

    path('attributes/', attributes_list, name='attribute-list'),
    path('attributes/<int:pk>/', attributes_detail, name='attributes-detail'),
]
