import json
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_yaml.parsers import YAMLParser

from .serializers import UserSerializer, LoginSerializer, ProductSerializer, ContactSerializer
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            token = Token.objects.create(user=user)
            return Response({'Status': 'OK', 'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'Status': 'OK', 'token': token.key}, status=status.HTTP_200_OK)


class CustomYamlParser(YAMLParser):
    media_type = "text/yaml"


class YAMLLoadView(APIView):
    parser_classes = (CustomYamlParser,)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {
                    'Error': 'Please register or provide token in headers',
                    'Format': '{Authorization: Token <your_token>} in headers'
                }
            )

        if request.user.type != 'seller':
            return Response({'Error': 'Available only for sellers'})

        try:
            data = request.data
            shop, created = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)

            for category in data['categories']:
                category_object, created = Category.objects.get_or_create(id=category['id'], name=category['name'])
                category_object.shops.add(shop.id)
                category_object.save()

            for item in data['goods']:
                product, created = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                product_info = ProductInfo.objects.create(
                    product_id=product.id,
                    external_id=item['id'],
                    model=item['model'],
                    name=item['name'],
                    price=item['price'],
                    price_rrp=item['price_rrc'],
                    quantity=item['quantity'],
                    shop_id=shop.id
                )
                for name, value in item['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(product_info_id=product_info.id,
                                                    parameter_id=parameter_object.id,
                                                    value=value)
        except Exception as e:
            return Response({'Status': 'Failed', 'Exception': str(e)})

        return Response({'Status': 'OK', 'data': data})


class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ContactView(APIView):

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': 'Failed', 'Error': 'Please register or login'})

        queryset = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': 'Failed', 'Error': 'Please register or login'})

        if {'first_name', 'city', 'street', 'phone'}.issubset(request.data):
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'Status': 'Success'})
            else:
                return Response({'Status': 'Failed', 'Error': serializer.errors})
        else:
            return Response({'Status': 'Failed', 'Error': 'Please add required fields'})

    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': 'Failed', 'Error': 'Please register or login'})

        id = request.data.get('id')
        if not id:
            return Response({'Status': 'Failed', 'Error': 'No id provided'})

        try:
            contact = Contact.objects.get(id=id, user_id=request.user.id)
        except Contact.DoesNotExist:
            return Response({'Status': 'Failed', 'Error': 'Contact not found'})

        contact.delete()
        return Response({'Status': 'Success', 'Message': 'Contact deleted successfully'})
