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

from truck_management_app.models import Truck
from truck_management_app.sertializers import TruckSerializer, TruckInfoSerializer

import stripe
from knox.models import AuthToken

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckAuthenticatedView(RetrieveAPIView):

    serializer_class = UserCRUDSerializer

    def get_object(self):
        return self.request.user

class CheckAuthenticatedDriverView(APIView):
    def post(self, request, token_id, format=None):
        try:
            driver = Driver.objects.get(email=request.data["email"])
            driver = DriverSerializer(driver).data
            return Response(driver, status=status.HTTP_200_OK)
        except:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)



class DriverLogoutView(APIView):
    def post(self, request, format=None):
        try:
            if request.data["email"] != request.data["token"]:
                return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)
            driver = Driver.objects.get(email=request.data["email"])
            print("SH")
            return Response({"Result":"Success"}, status=status.HTTP_200_OK)
        except:
            return Response({"Result": "Error"}, status=status.HTTP_400_BAD_REQUEST)

class SignupView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        password = data['password']
        re_password = data['re_password']

        result = dict()

        if password != re_password:
            return Response({"Result": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)


        user_serializer = self.get_serializer(data=data)
        if user_serializer.is_valid() == False:
            print(user_serializer.errors)
            return Response({"Result": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user = user_serializer.save()
        user.is_active = False
        # generate code here to send with email

        uid_token = urlsafe_base64_encode(force_bytes(user.pk))
        last_token = default_token_generator.make_token(user)

        user.last_uid=uid_token
        user.last_token=last_token
        user.last_token_password=urlsafe_base64_encode(force_bytes(uid_token))

        user.account_category = AccountCategory.objects.get(id=data['account_category_id'])

        time_for_subscription = data['time_for_subscription']

        if(user.account_category.title == "Simple Driver"):
            # If subscibed for the quarter
            if(int(time_for_subscription) > 0 and int(time_for_subscription) < 4):
                amount = 50 * int(time_for_subscription)
            else:
                # Discount of 20 USD if 4 quarters = 1 year
                amount=180

        elif (user.account_category.title == "Business Starter"):
            # If subscibed for the quarter
            if (int(time_for_subscription) > 0 and int(time_for_subscription) < 4):
                amount = 80 * int(time_for_subscription)
            else:
                # Discount of 20 USD if 4 quarters = 1 year
                amount = 300

        elif (user.account_category.title == "Professional Trucking"):
            # If subscibed for the quarter
            if (int(time_for_subscription) > 0 and int(time_for_subscription) < 4):
                amount = 150 * int(time_for_subscription)
            else:
                # Discount of 100 USD if 4 quarters = 1 year
                amount = 500


        # try:
        if True:

            card_num = request.data['card_num']
            exp_month = request.data['exp_month']
            exp_year = request.data['exp_year']
            cvc = request.data['cvc']

            token = stripe.Token.create(
                card={
                    "number": card_num,
                    "exp_month": int(exp_month),
                    "exp_year": int(exp_year),
                    "cvc": cvc
                },
            )

            if request.data['save_payment_info']:
                user.one_click_purchasing = True
                customer = stripe.Customer.create(
                    email=user.email,
                    source=token
                )

                user.stripe_customer_id = customer['id']
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    customer=user.stripe_customer_id
                )


            if request.data['save_payment_info'] == False:

                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=token
                )

            user.is_active = True
            user.save()
            payment = Payment(user=user, stripe_charge_id=charge['id'], amount=amount)
            payment.save()
            paid_untill = add_paid_quarters(int(time_for_subscription), datetime.today())
            user.paid_untill = paid_untill
            user.save()

            if(request.data['is_driving'] == True):
                print("Owner is drving")
                driver_serializer = DriverSerializer(data=data)
                if driver_serializer.is_valid() == False:
                    print(driver_serializer.errors)
                    return Response({"Result": driver_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                driver = driver_serializer.save()
                user.drivers.add(driver)
                user.save()

            if(int(time_for_subscription) == 1):
                unit_of_quarters = "quarter"
            elif (int(time_for_subscription) < 4):
                unit_of_quarters = "quarters"
            else:
                unit_of_quarters = "year"

            email_subject="Subscription Bought."
            message=render_to_string('user_account_app/subscription_bought.html', {
                'user': user.email,
                'total_amount':str(amount),
                "amount_of_quarters": time_for_subscription,
                "unit_of_quarters": unit_of_quarters,
                "paid_untill": user.paid_untill.strftime("%-d %B %Y"),
                # "uid": user.last_uid,
                # "token":user.last_token,
                # "account_password":user.last_token_password,
            })
            to_email = user.email
            email = EmailMultiAlternatives(email_subject, to=[to_email])
            email.attach_alternative(message, "text/html")
            email.send()



            #
            # admin_message=render_to_string('admin-purchase-made.html',{
            #     'user': order.user_email,
            #     'order': order.id,
            #     'current_admin_domain':current_admin_domain,
            # })
            #
            # to_admin_email = admin_email
            # email = EmailMultiAlternatives(email_subject, to=[to_admin_email])
            # email.attach_alternative(admin_message, "text/html")
            # email.send()

            result['user'] = UserCRUDSerializer(
                user,
                context = self.get_serializer_context()).data
            result['token'] = AuthToken.objects.create(user)[1]
            result['account_type'] = "COMPANY OWNER"

            return Response({'Result': result}, status=status.HTTP_200_OK)

        else:
            pass

        # except stripe.error.CardError as e:
        #     response = Response({"Result":"Error with card during payment"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # except stripe.error.RateLimitError as e:
        #     response = Response({"Result":"Rate Limit error during payment"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # except stripe.error.InvalidRequestError as e:
        #     response = Response({"Result":"Invalid request error during payment"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # except stripe.error.AuthenticationError as e:
        #     response = Response({"Result":"Authentication error during payment"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # except stripe.error.APIConnectionError as e:
        #     response = Response({"Result":"API connection error during payment"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # except stripe.error.StripeError as e:
        #     response = Response({"Result":"Something went wrong during payment"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # except:
        #     response = Response({"Result":"Error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return response

#===============================================================================
#   Helpers
#===============================================================================
def current_time_modified(current_time_date):
    today =  current_time_date
    today_year = current_time_date.year

    if today < datetime(today_year, 4, 30):
        return datetime(today_year, 4, 30)

    elif today < datetime(today_year, 7, 31):
        return datetime(today_year, 7, 31)

    elif today < datetime(today_year, 10, 31):
        return datetime(today_year, 10, 31)

    else:
        return datetime(today_year+1, 1, 31)
#===============================================
def add_paid_quarters(quarters, current_time_date):
    if quarters == 1:
        return current_time_date
    elif quarters == 2:
        current_time_date = current_time_date + relativedelta(months = 3)
        return current_time_modified(current_time_date)
    elif quarters == 3:
        current_time_date = current_time_date + relativedelta(months = 6)
        return current_time_modified(current_time_date)
    else:
        current_time_date = current_time_date + relativedelta(months = 9)
        return current_time_modified(current_time_date)




class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        data = request.data
        result = dict()

        try:
            user_serializer = self.get_serializer(data=data)

            if user_serializer.is_valid() == False:
                try:
                    #     Try to find driver
                    driver = Driver.objects.get(email=data["email"], password=data['password']);
                    result['user'] = DriverSerializer(driver).data
                    result['token'] = driver.email
                    result['account_type'] = "DRIVER"
                    return Response({'Result': result}, status=status.HTTP_201_CREATED)
                except:
                    return Response({'Result': "No user with that credentials"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = user_serializer.validated_data
                result['user'] = UserCRUDSerializer(
                    user,
                    context=self.get_serializer_context()).data
                result['token'] = AuthToken.objects.create(user)[1]
                result['account_type'] = "COMPANY OWNER"
                return Response({'Result': result}, status=status.HTTP_201_CREATED)
        except:
            return Response({'Result': "Error with user credentials"}, status=status.HTTP_400_BAD_REQUEST)







#===============================================================================
#   Account Category List
#===============================================================================
class AccountCategoryListView(ListAPIView):
    serializer_class = AccountCategorySerializer
    model = AccountCategory
    queryset = AccountCategory.objects.all()


class AccountCategoryRetrieveView(RetrieveAPIView):
    serializer_class = AccountCategorySerializer
    model = AccountCategory
    lookup_field = 'id'
    queryset = AccountCategory.objects.all()


class UserInformationView(APIView):

    def get(self, request, id, format=None):

        user = User.objects.get(id=id)
        trucks = Truck.objects.filter(owner=user)
        if(trucks):
            trucks = TruckInfoSerializer(trucks, many=True).data
        else:
            trucks = {}

        account_category = user.account_category
        account_category = AccountCategorySerializer(account_category).data

        drivers = user.drivers.all()
        if(drivers):
            drivers = DriverSerializer(drivers, many=True).data
        else:
            drivers = {}

        return Response({"trucks":trucks, "account_category": account_category, "drivers": drivers}, status=status.HTTP_200_OK)


class CreateNewTruck(APIView):

    def post(self, request, id, format=None):
        user = User.objects.get(id=id)
        truck = Truck(plate=request.data['plate'], nickname=request.data['nickname'], owner=user, current_driver=None)
        truck.save()
        if request.data["driver"] == "None" or request.data["driver"] == None:
            truck.current_driver = None
        else:
            driver = Driver.objects.get(email = request.data["driver"])
            truck.current_driver = driver
        truck.save()
        return Response({"Result":"Success"}, status=status.HTTP_200_OK)



class UpdateTruckInfo(APIView):
    def post(self, request, id, truck_id, format=None):
        user = User.objects.get(id=id)
        truck = Truck.objects.get(id=truck_id)
        truck.plate = request.data["plate"]
        truck.nickname = request.data["nickname"]
        truck.save()


        if request.data["driver"] == "None" or request.data["driver"] == None:
            truck.current_driver = None
        else:
            driver = Driver.objects.get(email = request.data["driver"])
            truck.current_driver = driver
        truck.save()
        return Response({"Result":"Success"}, status=status.HTTP_200_OK)


class deleteDriverFromCompany(APIView):

    def post(self, request, id, driver_id, format=None):
        user = User.objects.get(id=id)
        driver = Driver.objects.get(id=driver_id)

        trucks = Truck.objects.filter(owner=user, current_driver=driver)

        for truck in trucks:
            truck.current_driver=None
            truck.save()

        user.drivers.remove(driver)
        user.save()

        return Response({"Result": "Success"}, status=status.HTTP_200_OK)



class deleteTruckFromCompany(APIView):

    def post(self, request, id, truck_id, format=None):
        user = User.objects.get(id=id)
        truck = Truck.objects.get(id=truck_id)
        truck.delete()

        return Response({"Result": "Success"}, status=status.HTTP_200_OK)


