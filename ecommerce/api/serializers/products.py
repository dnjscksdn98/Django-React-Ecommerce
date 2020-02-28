from rest_framework import serializers

from ecommerce.models import Item, Option, OptionValue


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
