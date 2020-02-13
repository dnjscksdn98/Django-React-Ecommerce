from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ecommerce.models import Item, Order, OrderItem
from .serializers import ItemSerializer, OrderSerializer


class ItemListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({'message': 'Invalid request.'}, status=HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, slug=slug)
        # get_or_create : returns a tuple
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_queryset = Order.objects.filter(user=request.user, ordered=False)

        # if there is an active order
        if order_queryset.exists():
            order = order_queryset.first()
            # if the item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                return Response(status=HTTP_200_OK)

            # if it is not in the order
            else:
                order.items.add(order_item)
                return Response(status=HTTP_200_OK)

        # if there is no active order
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response(status=HTTP_200_OK)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order

        except ObjectDoesNotExist:
            return Response({'message': 'You do not have an active order.'}, status=HTTP_400_BAD_REQUEST)
