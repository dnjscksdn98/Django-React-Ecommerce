from rest_framework import serializers
from django_countries.serializer_fields import CountryField

from ecommerce.models import Item, OrderItem, Order, Coupon, Address


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'amount'
        ]


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'price',
            'discount_price',
            'category',
            'label',
            'slug',
            'description',
            'image'
        ]

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()


class OrderItemSerializer(serializers.ModelSerializer):
    item = StringSerializer()
    item_obj = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'item',
            'quantity',
            'final_price',
            'item_obj'
        ]

    def get_item_obj(self, obj):
        return ItemSerializer(obj.item).data

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
