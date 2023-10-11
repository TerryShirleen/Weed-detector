 
from django.urls import path, include
#from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from rest_framework import routers
from.views import *
urlpatterns = [
    path('', views.index, name='index'),
    path('account/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<username>/', views.profile, name='profile'),
    path('profile/<username>/edit/', views.edit_profile, name='edit_profile'),
    path('user_approve/<int:id>', views.user_approve,name='user_approve'),
    path('user_detail/<int:id>/', views.user_detail,name='user_detail'),
    path('verified_users', views.verified_users,name="verified_users"),
    path('all_users', views.all_users,name="all_users"),
    path('otp_verification/', views.otp_verification, name='otp_verification'),

]