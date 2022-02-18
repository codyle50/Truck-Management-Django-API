from django.contrib import admin
from django.conf.urls import url,include
from .views import *

app_name = 'truck_management_app'

urlpatterns = [
    url(r'^new-entry/(?P<truck_id>[0-9]+)/$', NewEntryView.as_view(), name='new-entry-api'),
    url(r'^all-entries/(?P<owner_id>[0-9]+)/(?P<truck_id>[0-9]+)/$', ListAllQuarterEntry.as_view(), name='list-all-new-entries-api'),
]
