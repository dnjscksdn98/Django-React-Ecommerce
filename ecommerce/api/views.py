from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.http import Http404
from django_countries import countries

from ecommerce.models import Item, Order, OrderItem, Payment, UserProfile, Coupon, Address, Option, OptionValue
from .serializers import ItemSerializer, OrderSerializer, AddressSerializer, PaymentSerializer, ItemDetailSerializer

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)


class ItemListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class ItemDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ItemDetailSerializer
    queryset = Item.objects.all()


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        options = request.data.get('options', [])
        if slug is None:
            return Response({'message': 'Invalid request.'}, status=HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, slug=slug)

        minimum_option_count = Option.objects.filter(item=item).count()
        if len(options) < minimum_option_count:
            return Response({'message': 'Please specify the required options.'}, status=HTTP_400_BAD_REQUEST)

        # get_or_create : returns a tuple
        order_item_queryset = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False
        )

        for option in options:
            order_item_queryset = order_item_queryset.filter(
                item_options__exact=option
            )

        if order_item_queryset.exists():
            order_item = order_item_queryset.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                ordered=False
            )
            order_item.item_options.add(*options)
            order_item.save()

        order_queryset = Order.objects.filter(user=request.user, ordered=False)
        # if there is an active order
        if order_queryset.exists():
            order = order_queryset.first()

            # if it is not in the order
            if not order.items.filter(item__id=order_item.id).exists():
                order.items.add(order_item)
            return Response(status=HTTP_200_OK)

        # if there is no active order
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response(status=HTTP_200_OK)


class SubtractItemQuantityView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({'message': 'Invalid data'}, status=HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, slug=slug)
        order_queryset = Order.objects.filter(user=request.user, ordered=False)

        if order_queryset.exists():
            order = order_queryset.first()
            # check if the item exists in the order
            if order.items.filter(item__slug=slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item, user=request.user, ordered=False).first()

                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    return Response({'message': 'This item quantity was updated.'}, status=HTTP_200_OK)

                else:
                    order.items.remove(order_item)
                    return Response({'message': 'This item quantity was updated.'}, status=HTTP_200_OK)

            else:
                return Response({'message': 'This item was not in your cart.'}, status=HTTP_400_BAD_REQUEST)

        else:
            return Response({'message': 'You do not have an active order.'}, status=HTTP_400_BAD_REQUEST)


class OrderItemDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # fetching the queryset
    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order

        except ObjectDoesNotExist:
            raise Http404('You do not have an active order.')


class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        userprofile = UserProfile.objects.get(user=self.request.user)
        token = request.data.get('stripeToken')
        billing_address_id = request.data.get('defaultBillingAddress')
        shipping_address_id = request.data.get('defaultShippingAddress')
        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)

        # if stripe id already exists
        if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(
                userprofile.stripe_customer_id)
            customer.sources.create(source=token)

        # if stripe id doesn't exist
        else:
            customer = stripe.Customer.create(
                email=self.request.user.email,
            )
            customer.sources.create(source=token)
            userprofile.stripe_customer_id = customer['id']
            userprofile.one_click_purchasing = True
            userprofile.save()

        amount = int(order.get_total() * 100)

        try:
            # charge the customer because we cannot charge the token more than once
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                customer=userprofile.stripe_customer_id
            )

            # create the payment
            payment = Payment(
                stripe_charge_id=charge['id'],
                user=self.request.user,
                amount=order.get_total()
            )
            payment.save()

            # assign the payment to the order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"message": "Something went wrong. You were not charged. Please try again."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            # send an email to ourselves
            return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)


class PaymentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)

        if code is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)

        order = Order.objects.get(
            user=request.user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)


class AddressListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    # fetch the requested queryset
    def get_queryset(self):
        queryset = Address.objects.all()

        # get the param from the URL
        address_type = self.request.query_params.get('address_type', None)

        # if param doesn't exist
        if address_type is None:
            return queryset

        # return the filtered queryset
        return queryset.filter(user=self.request.user, address_type=address_type)


class AddressCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def post(self, request, *args, **kwargs):
        form = request.data.get('formData', None)
        if form is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)

        address_type = request.data.get('address_type')
        address = Address(
            user=request.user,
            street_address=form['street_address'],
            apartment_address=form['apartment_address'],
            country=form['country'],
            zip=form['zip'],
            address_type=address_type,
            default=form['default']
        )

        current_default_address = Address.objects.filter(
            user=request.user, default=True, address_type=address_type)
        if current_default_address.exists() and address.default == True:
            current_default_address = current_default_address.first()
            current_default_address.default = False
            current_default_address.save()

        address.save()
        return Response(status=HTTP_200_OK)


class AddressUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def put(self, request, *args, **kwargs):
        form = request.data.get('formData', None)
        if form is None:
            return Response({'message': 'Invalid data received'}, status=HTTP_400_BAD_REQUEST)

        id = form['id']
        default = form['default']
        address_type = request.data.get('address_type')
        address = Address.objects.get(
            id=id, user=request.user, address_type=address_type)
        current_default_address = Address.objects.filter(
            user=request.user, default=True, address_type=address_type)

        if current_default_address.exists() and default == True:
            current_default_address = current_default_address.first()
            current_default_address.default = False
            current_default_address.save()

        address.street_address = form['street_address']
        address.apartment_address = form['apartment_address']
        address.country = form['country']
        address.zip = form['zip']
        address.default = default
        address.save()
        return Response(status=HTTP_200_OK)


class AddressDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.all()


class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(countries, status=HTTP_200_OK)
