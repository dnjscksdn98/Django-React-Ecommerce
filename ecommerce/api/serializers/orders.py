from rest_framework import serializers

from ecommerce.models import OrderItem, Order
from ecommerce.api.serializers.products import ItemSerializer, OptionValueDetailSerializer
from ecommerce.api.serializers.serializers import CouponSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    # item = StringSerializer()
    item = serializers.SerializerMethodField()
    item_options = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'item',
            'item_options',
            'quantity',
            'final_price'
        ]

    def get_item(self, obj):
        return ItemSerializer(obj.item).data

    def get_item_options(self, obj):
        return OptionValueDetailSerializer(obj.item_options.all(), many=True).data

    def get_final_price(self, obj):
        return obj.get_final_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'order_items',
            'total',
            'coupon'
        ]

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None
