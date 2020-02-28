from rest_framework import serializers

from ecommerce.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'timestamp'
        ]
