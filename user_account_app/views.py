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

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import authentication_classes, permission_classes

from .models import *
from .serializers import *

import stripe
from knox.models import AuthToken

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckAuthenticatedView(RetrieveAPIView):

    serializer_class = UserCRUDSerializer

    def get_object(self):
        print(self.request)
        return self.request.user



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

        user.last_uid=urlsafe_base64_encode(force_bytes(user.pk))
        user.last_token=default_token_generator.make_token(user)

        user.account_category = AccountCategory.objects.get(id=data['account_category_id'])

        time_for_subscription = data['time_for_subscription']

        if(user.account_category.title == "Simple Driver"):
            # If subscibed for the quarter
            if(time_for_subscription == 1):
                amount=50
            else:
                amount=200


        # Create payment and activate user

        try:

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
            if time_for_subscription == 1:

                if datetime.today() < datetime(datetime.today().year, 4, 30):
                    user.paid_untill = datetime(datetime.today().year, 4, 30)

                elif datetime.today() < datetime(datetime.today().year, 7, 31):
                    user.paid_untill = datetime(datetime.today().year, 7, 31)

                elif datetime.today() < datetime(datetime.today().year, 10, 31):
                    user.paid_untill = datetime(datetime.today().year, 10, 31)
                    print(user.paid_untill)

                else:
                    user.paid_untill = datetime(datetime.today().year+1, 1, 31)
            else:
                user.paid_untill = datetime(datetime.today().year+1, 1, 31)

            user.save()

            # email_subject="Purchase made."
            # message=render_to_string('purchase-made.html', {
            #     'user': order.user_email,
            #     'image': order.product.product.image,
            #     'amount_of_product': str(order.product.amount),
            #     'total_amount':str("{:.2f}".format(order.get_total_price())),
            # })
            # to_email = order.user_email
            # email = EmailMultiAlternatives(email_subject, to=[to_email])
            # email.attach_alternative(message, "text/html")
            # email.send()
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

            return Response({'Result': result}, status=status.HTTP_200_OK)

        except stripe.error.CardError as e:
            response = Response({"Result":"Error with card during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            response = Response({"Result":"Rate Limit error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            response = Response({"Result":"Invalid request error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            response = Response({"Result":"Authentication error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            response = Response({"Result":"API connection error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            response = Response({"Result":"Something went wrong during payment"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            response = Response({"Result":"Error during payment"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return response







class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        data = request.data
        result = dict()

        # try:
        if True:
            user_serializer = self.get_serializer(data=data)

            if user_serializer.is_valid() == False:
                return Response({'Result': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = user_serializer.validated_data
                result['user'] = UserCRUDSerializer(
                    user,
                    context=self.get_serializer_context()).data
                result['token'] = AuthToken.objects.create(user)[1]
                return Response({'Result': result}, status=status.HTTP_201_CREATED)
        # except:
        else:
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
