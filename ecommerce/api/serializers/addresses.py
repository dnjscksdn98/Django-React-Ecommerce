from rest_framework import serializers
from django_countries.serializer_fields import CountryField

from ecommerce.models import Address


class AddressSerializer(serializers.ModelSerializer):
    country = CountryField()

    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'street_address',
            'apartment_address',
            'country',
            'zip',
            'address_type',
            'default'
        ]
