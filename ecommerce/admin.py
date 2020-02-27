from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile, Option, OptionValue


# create custom action
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


def make_being_delivered(modeladmin, request, queryset):
    queryset.update(being_delivered=True)


make_being_delivered.short_description = 'Update orders to being delivered'


def make_order_received(modeladmin, request, queryset):
    queryset.update(being_delivered=False, received=True)


make_order_received.short_description = 'Update orders to received'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    ]
    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    ]
    list_filter = [
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [
        make_refund_accepted,
        make_being_delivered,
        make_order_received
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = [
        'default',
        'address_type',
        'country'
    ]
    search_fields = [
        'user',
        'street_address',
        'apartment_address',
        'zip'
    ]


class OptionValueAdmin(admin.ModelAdmin):
    list_display = [
        'option',
        'value',
        'additional_price',
        'attachment'
    ]
    list_filter = [
        'option',
        'option__item'
    ]
    search_fields = [
        'value'
    ]


class OptionValueInlineAdmin(admin.TabularInline):
    model = OptionValue
    extra = 1


class OptionAdmin(admin.ModelAdmin):
    list_display = [
        'item',
        'name'
    ]
    list_filter = [
        'item'
    ]
    search_fields = [
        'name'
    ]
    inlines = [OptionValueInlineAdmin]


admin.site.register(Item)
admin.site.register(Option, OptionAdmin)
admin.site.register(OptionValue, OptionValueAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
