from django.urls import path
from .views import (
    ItemListView,
    AddToCartView,
    SubtractItemQuantityView,
    OrderItemDeleteView,
    OrderDetailView,
    PaymentView,
    PaymentListView,
    AddCouponView,
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    CountryListView,
    UserIDView
)

urlpatterns = [
    path('product-list/', ItemListView.as_view(), name='product-list'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('order-item/subtract/',
         SubtractItemQuantityView.as_view(), name='order-item-subtract'),
    path('order-item/<pk>/delete/',
         OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('checkout/', PaymentView.as_view(), name='checkout'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('address/list/', AddressListView.as_view(), name='address-list'),
    path('address/create/', AddressCreateView.as_view(), name='address-create'),
    path('address/<pk>/update/', AddressUpdateView.as_view(), name='address-update'),
    path('address/<pk>/delete/', AddressDeleteView.as_view(), name='address-delete'),
    path('country/list/', CountryListView.as_view(), name='country-list'),
    path('user/id/', UserIDView.as_view(), name='user-id')
]
