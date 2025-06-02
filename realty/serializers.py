from rest_framework import serializers
from .models import RentHome, Attribute, Address

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'city', 'street', 'house_number']

class RentHomeSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        required=False,
        allow_null=True
    )
    attributes = AttributeSerializer(many=True, read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = RentHome
        fields = [
            'id', 'title', 'description', 'address', 'rooms', 'beds', 'area',
            'price', 'distance_to_sea', 'distance_to_center', 'distance_to_transport',
            'attributes'
        ]

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        rent_home = RentHome.objects.create(**validated_data)
        if address_data:
            address, _ = Address.objects.get_or_create(**address_data)
            rent_home.address = address
            rent_home.save()
        return rent_home