from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.shortcuts import get_object_or_404
from django.utils import timezone

from ecommerce.models import Item, Option
from ecommerce.api.serializers.products import ItemSerializer, ItemDetailSerializer


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
