
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *
from django.contrib import auth

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name','stripe_customer_id','phone', 'company_name', 'zip_code', 'usa_state']
        extra_kwargs = {'password':{'witre_only':True, 'required':True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class UserCRUDSerializer(serializers.ModelSerializer):

    email = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance
