from django.contrib import admin
from django.conf.urls import url,include
from .views import *

from knox import views as knox_views

app_name = 'user_account_app'

urlpatterns = [
    url(r'^logout/$', knox_views.LogoutView.as_view(), name='knox-logout-api'),
    url(r'^signup/$', SignupView.as_view(), name='sign-up-api'),
    url(r'^login/$', LoginView.as_view(), name='login-api'),
    url(r'^check-auth/$', CheckAuthenticatedView.as_view(), name='check-auth-api'),
    url(r'^subscriptions/$', AccountCategoryListView.as_view(), name='account-category-list-api'),
    url(r'^subscriptions/(?P<id>[0-9]+)/$', AccountCategoryRetrieveView.as_view(), name='account-category-retrieve-api'),
]
