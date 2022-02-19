from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.contrib import auth
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

import json
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import authentication_classes, permission_classes

from .models import *
from .serializers import *

from user_account_app.models import User, Driver


# Create your views here.

class NewEntryView(APIView):

    def post(self, request, truck_id, format=None):
        data = request.data

        day = data['day']
        month = data['month']
        year = data['year']

        current_quarter = 1
        if month > 3:
            current_quarter = 2
        if month > 6:
            current_quarter = 3
        if month > 9:
            current_quarter = 4

        # try:
        if(True):
            truck = Truck.objects.get(id=truck_id)
            try:
                driver = Driver.objects.get(email=data['driver'])
            except:
                driver = User.objects.get(email = data['driver'])

            new_entry = NewEntrySerializer(data=data)
            if new_entry.is_valid() == False:
                return Response({"Result": new_entry.errors}, status=status.HTTP_400_BAD_REQUEST)


            new_entry = new_entry.save()

            try:
                new_entry.driver = driver
            except:
                pass
            new_entry.quarter_number = current_quarter
            new_entry.truck=truck
            new_entry.save()



            try:
                quarter = Quarter.objects.get(number = current_quarter, year=year, truck=truck)
            except:
                quarter = Quarter(number = current_quarter, year=year, truck=truck)
                quarter.save()

            quarter.total_toll_miles = quarter.total_toll_miles + new_entry.total_toll_miles
            quarter.total_non_toll_miles = quarter.total_non_toll_miles + new_entry.total_non_toll_miles
            quarter.total_gallons = quarter.total_gallons + new_entry.total_gallons
            quarter.save()

            try:
                state_report = StateReport.objects.get(quarter=quarter, name=data['usa_state'], initials=data['initials'])
            except:
                state_report = StateReport(quarter=quarter, name=data['usa_state'], initials=data['initials'])
                state_report.save()

            state_report.total_toll_miles = state_report.total_toll_miles + new_entry.total_toll_miles
            state_report.total_non_toll_miles = state_report.total_non_toll_miles + new_entry.total_non_toll_miles
            state_report.total_gallons = state_report.total_gallons + new_entry.total_gallons
            state_report = state_report.save()
            return Response({"Result": "Success"}, status=status.HTTP_200_OK)


        # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)






class ListAllQuarterEntry(APIView):

    def post(self, request, owner_id, truck_id, format=None):

        # try:
        if(True):
            owner = User.objects.get(id=owner_id)
            truck = Truck.objects.get(owner=owner, id=truck_id)

            month = request.data['month']
            year = request.data['year']

            current_quarter = 1
            if month > 3:
                current_quarter = 2
            if month > 6:
                current_quarter = 3
            if month > 9:
                current_quarter = 4

            new_entries = NewEntry.objects.filter(truck=truck, year=year, current_quarter=current_quarter)

            new_entries_serializer = NewEntrySerializerComplex(new_entries, many=True).data
            return Response(new_entries_serializer, status=status.HTTP_200_OK)


        # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)






class CalculateQuarterTaxesView(APIView):

    def post(self, request, owner_id, truck_id, format=None):
        if (True):
            owner = User.objects.get(id=owner_id)
            truck = Truck.objects.get(owner=owner, id=truck_id)

            month = request.data['month']
            year = request.data['year']

            current_quarter = 1
            if month > 3:
                current_quarter = 2
            if month > 6:
                current_quarter = 3
            if month > 9:
                current_quarter = 4

            quarter = Quarter.objects.get(number = current_quarter, year=year, truck=truck)

            mpg = quarter.total_toll_miles / quarter.total_gallons
            quarter.total_mpg = round(mpg,2)
            quarter.save()

            quarter_fuel_tax_owned = 0

            state_reports = StateReport.objects.filter(quarter = quarter)
            for state_report in state_reports:
                tax_gallons = state_report.total_toll_miles / mpg
                state_tax = StateTaxes.objects.get(name = state_report.name ,number = current_quarter, year=year)
                net_tax_gallons = tax_gallons - state_report.total_gallons
                state_report.fuel_tax_owned = net_tax_gallons * state_tax.tax
                print(net_tax_gallons)
                print(net_tax_gallons * state_tax.tax)
                state_report.save()
                quarter_fuel_tax_owned = quarter_fuel_tax_owned + state_report.fuel_tax_owned

            quarter.fuel_tax_owned = quarter_fuel_tax_owned
            quarter.save()

            quarter_serializer = QuarterReportSerializer(quarter).data
            state_reports_serializer = StateReportSerializer(state_reports, many=True).data

            print(quarter_serializer)
            print(state_reports_serializer)

            return Response({"Quarter":quarter_serializer, "State_Reports": state_reports_serializer}, status=status.HTTP_200_OK)

            # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)



