from django.urls import path
from .views import *
urlpatterns = [
    path('dashboard_view/', dashboard_view, name='dashboard_view'),
    path('members_view/', members_view, name='members_view'),
    path('profile_view/', profile_view, name='profile_view'),
    path('', login_view, name='login_view'),
    path('forgot_password_view/', forgot_password_view, name='forgot_password_view'),
    path('otp_varification_view/', otp_varification_view, name='otp_varification_view'),
    path('logout/',logout,name='logout'),
    path('members_login_view/',members_login_view,name='members_login_view'),
    path('members_dashboard_view/',members_dashboard_view,name='members_dashboard_view'),
    path('members_profile_view/',members_profile_view,name='members_profile_view'),
    path('update_member_view/<int:id>',update_member_view,name='update_member_view'),
    path('delete_member_view/<int:id>',delete_member_view,name='delete_member_view'),
    path('income_view/',income_view,name='income_view'),
    path('members_income_view/',members_income_view,name='members_income_view'),
]
