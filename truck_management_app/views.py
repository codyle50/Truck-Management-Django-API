from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib import auth
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django import template
from django.template.loader import get_template
from django.core.files import File

import cgi, html
cgi.escape = html.escape

import json
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from io import BytesIO
from xhtml2pdf import pisa
import os

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import authentication_classes, permission_classes

from .models import *
from .serializers import *

from user_account_app.models import User, Driver

from ifta_filing_django_api.settings import ROOT_BASE_DIR

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
                state_report.save()
                quarter_fuel_tax_owned = quarter_fuel_tax_owned + state_report.fuel_tax_owned

            quarter.fuel_tax_owned = quarter_fuel_tax_owned
            quarter.save()

            quarter_serializer = QuarterReportSerializer(quarter).data
            state_reports_serializer = StateReportSerializer(state_reports, many=True).data

            return Response({"Quarter":quarter_serializer, "State_Reports": state_reports_serializer}, status=status.HTTP_200_OK)

            # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)



class AllTimesTaxesYear(APIView):

    def get(self, request, owner_id, truck_id, format=None):

        # try:
        if(True):
            owner = User.objects.get(id=owner_id)
            truck = Truck.objects.get(owner=owner, id=truck_id)

            years = Quarter.objects.filter(truck=truck).values("year")

            all_taxes_years = set()

            for year in years:
                all_taxes_years.add(year["year"])

            return Response({"Result": all_taxes_years}, status=status.HTTP_200_OK)

            # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)


class YearTaxes(APIView):

    def get(self, request, owner_id, truck_id, year, format=None):

        # try:
        if(True):
            owner = User.objects.get(id=owner_id)
            truck = Truck.objects.get(owner=owner, id=truck_id)

            print(year)

            quarters = Quarter.objects.filter(truck=truck, year=year).values("number")

            quarters_set = set()

            for quarter in quarters:
                quarters_set.add(quarter["number"])

                print(quarter)

            return Response({"Result": quarters_set}, status=status.HTTP_200_OK)

            # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)


class QuarterTaxes(APIView):

    def post(self, request, owner_id, truck_id, year, number, format=None):
        if (True):
            owner = User.objects.get(id=owner_id)
            truck = Truck.objects.get(owner=owner, id=truck_id)

            current_quarter = number

            quarter = Quarter.objects.get(number = current_quarter, year=year, truck=truck)

            mpg = quarter.total_toll_miles / quarter.total_gallons
            quarter.total_mpg = round(mpg,2)
            quarter.save()

            quarter_fuel_tax_owned = 0

            state_reports = StateReport.objects.filter(quarter = quarter)

            this_year = request.data['year']
            this_month = request.data['month']

            this_quarter = 1
            if this_month > 3:
                this_quarter = 2
            if this_month > 6:
                this_quarter = 3
            if this_month > 9:
                this_quarter = 4

            if(this_year != year or this_quarter != current_quarter):

                for state_report in state_reports:
                    tax_gallons = state_report.total_toll_miles / mpg
                    state_tax = StateTaxes.objects.get(name = state_report.name ,number = current_quarter, year=year)
                    net_tax_gallons = tax_gallons - state_report.total_gallons
                    state_report.fuel_tax_owned = net_tax_gallons * state_tax.tax
                    state_report.save()
                    quarter_fuel_tax_owned = quarter_fuel_tax_owned + state_report.fuel_tax_owned

                quarter.fuel_tax_owned = quarter_fuel_tax_owned
                quarter.save()

            quarter_serializer = QuarterReportSerializer(quarter).data
            state_reports_serializer = StateReportSerializer(state_reports, many=True).data

            return Response({"Quarter":quarter_serializer, "State_Reports": state_reports_serializer}, status=status.HTTP_200_OK)

            # except:
        else:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)




def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class SendTaxesPDF(APIView):
    def post(self, request, owner_id, truck_id, format=None):

        this_year = request.data['year']
        this_month = request.data['month']

        this_quarter = 1
        if this_month > 3:
            this_quarter = 2
        if this_month > 6:
            this_quarter = 3
        if this_month > 9:
            this_quarter = 4

        user = User.objects.get(id=owner_id)
        truck = Truck.objects.get(id=truck_id)

        quarter = Quarter.objects.get(number=this_quarter, year=this_year, truck=truck)
        state_reports = StateReport.objects.filter(quarter=quarter)

        context = {"quarter": quarter, "state_reports":state_reports}
        pdf = render_to_pdf('truck_management_app/ifta_report.html',context_dict=context)
        filename = "YourPDF_Order{%s}.pdf" %(user.email)

        try:
            quarter.pdf.storage.delete(quarter.pdf.name)
        except:
            pass

        quarter.pdf.save(filename, File(BytesIO(pdf.content)))
        quarter.save()

        email = EmailMessage(
            'Ifta Report', 'Here is your Ifta report created by Ifta Filing', [user.email])
        email.attach_file(os.path.join(ROOT_BASE_DIR, 'media', str(quarter.pdf)))
        email.send()

        return Response({"Result": "Success"}, status=status.HTTP_200_OK)