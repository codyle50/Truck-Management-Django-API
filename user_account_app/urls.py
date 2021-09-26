from django.contrib import admin
from django.conf.urls import url,include
from .views import *

from knox import views as knox_views

app_name = 'user_account_app'

urlpatterns = [
    url(r'^logout/$', knox_views.LogoutView.as_view(), name='knox-logout-api'),
]
