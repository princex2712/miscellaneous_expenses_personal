from django.urls import path
from .views import *
urlpatterns = [
    path('', dashboard_view, name='dashboard_view'),
    path('members_view/', members_view, name='members_view'),
    path('profile_view/', profile_view, name='profile_view'),
]
