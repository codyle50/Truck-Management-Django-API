from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *
from django.contrib import auth

from user_account_app.models import Driver

class DriverSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields = ['email', 'first_name', 'last_name' ]

class TruckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Truck
        fields = '__all__'

class TruckInfoSerializer(serializers.ModelSerializer):

    current_driver = DriverSimpleSerializer()

    class Meta:
        model = Truck
        fields = '__all__'

class NewEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = NewEntry
        exclude  = ('truck', 'driver',)

class NewEntrySerializerComplex(serializers.ModelSerializer):

    driver = DriverSimpleSerializer()

    class Meta:
        model = NewEntry
        exclude = ( 'truck', )

class QuarterReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quarter
        exclude = ( 'truck', )


class StateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateReport
        exclude = ('quarter',)