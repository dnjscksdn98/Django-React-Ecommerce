from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from ecommerce.models import Address
from ecommerce.api.serializers import AddressSerializer


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
