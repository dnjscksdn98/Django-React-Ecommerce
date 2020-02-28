from rest_framework.generics import DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from ecommerce.models import Order, OrderItem
from ecommerce.api.serializers.orders import OrderSerializer


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


class OrderItemDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
