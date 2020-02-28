from rest_framework import serializers

from ecommerce.models import Coupon


# class StringSerializer(serializers.StringRelatedField):
#     def to_internal_value(self, value):
#         return value

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'amount'
        ]
