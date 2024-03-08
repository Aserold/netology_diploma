from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ProductInfo, Product, ProductParameter, Contact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_name', 'first_name', 'email', 'password', 'type']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                return {'user': user}
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()
    product_parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['name', 'shop', 'product_parameters', 'price', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'product_info']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id', 'last_name', 'first_name', 'surname', 'email', 'phone', 'city', 'street', 'building', 'housing', 'structure', 'apartment', 'user'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'user': {'write_only': True}
        }

