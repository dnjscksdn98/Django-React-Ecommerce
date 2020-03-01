from rest_framework import serializers
from django_countries.serializer_fields import CountryField

from ecommerce.models import Address, Item, Order, OrderItem, Coupon, Option, OptionValue, Payment


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
            'short_description',
            'long_description',
            'image'
        ]

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()


class OptionSerializer(serializers.ModelSerializer):
    item_options = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = [
            'id',
            'name',
            'item_options'
        ]

    def get_item_options(self, obj):
        return OptionValueSerializer(obj.optionvalue_set.all(), many=True).data


class OptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionValue
        fields = [
            'id',
            'value',
            'additional_price',
            'default',
            'attachment'
        ]


class ItemDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

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
            'short_description',
            'long_description',
            'image',
            'options'
        ]

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()

    def get_options(self, obj):
        return OptionSerializer(obj.option_set.all(), many=True).data


class OptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = [
            'id',
            'name'
        ]


class OptionValueDetailSerializer(serializers.ModelSerializer):
    option = serializers.SerializerMethodField()

    class Meta:
        model = OptionValue
        fields = [
            'id',
            'option',
            'value',
            'additional_price',
            'default',
            'attachment'
        ]

    def get_option(self, obj):
        return OptionDetailSerializer(obj.option).data


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


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'amount',
            'timestamp'
        ]

    def get_order(self, obj):
        return OrderSerializer(obj.order_set.all()).data


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
