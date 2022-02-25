from django.contrib import admin
from django.conf.urls import url,include
from .views import *

from knox import views as knox_views

app_name = 'user_account_app'

urlpatterns = [
    url(r'^logout/$', knox_views.LogoutView.as_view(), name='knox-logout-api'),
    url(r'^driver/logout/$', DriverLogoutView.as_view(), name='driver-logout-api'),
    url(r'^signup/$', SignupView.as_view(), name='sign-up-api'),
    url(r'^login/$', LoginView.as_view(), name='login-api'),
    url(r'^check-auth/$', CheckAuthenticatedView.as_view(), name='check-auth-api'),
    url(r'^driver/check-auth/(?P<token_id>\w+|[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', CheckAuthenticatedDriverView.as_view(), name='check-driver-auth-api'),
    url(r'^subscriptions/$', AccountCategoryListView.as_view(), name='account-category-list-api'),
    url(r'^subscriptions/(?P<id>[0-9]+)/$', AccountCategoryRetrieveView.as_view(), name='account-category-retrieve-api'),
    url(r'^account-info/(?P<id>[0-9]+)/$', UserInformationView.as_view(), name='account-info-api'),
    url(r'^create-new-truck/(?P<id>[0-9]+)/$', CreateNewTruck.as_view(), name='create-new-truck-api'),
    url(r'^update-truck-info/(?P<id>[0-9]+)/(?P<truck_id>[0-9]+)/$', UpdateTruckInfo.as_view(), name='update-truck-info-api'),
    url(r'^delete-company-driver/(?P<id>[0-9]+)/(?P<driver_id>[0-9]+)/$', deleteDriverFromCompany.as_view(), name='delete-driver-company-api'),
    url(r'^delete-company-truck/(?P<id>[0-9]+)/(?P<truck_id>[0-9]+)/$', deleteTruckFromCompany.as_view(), name='delete-truck-company-api'),
    url(r'^reset-password/(?P<id>[0-9]+)/$', ResetPasswordView.as_view(), name='reset-password-api'),
    url(r'^extend-subscription/(?P<id>[0-9]+)/$', ExtendSubscription.as_view(), name='reset-password-api'),
    url(r'^edit-account-info/(?P<id>[0-9]+)/$', EditUserAccountInfoView.as_view(), name='edit-account-info-api'),
    url(r'^add-driver/(?P<id>[0-9]+)/$', AddDriverRequestView.as_view(), name='add-driver-api'),
    url(r'^driver-sign-up/$', RegisterDriver.as_view(), name='driver-sign-up-api'),
]