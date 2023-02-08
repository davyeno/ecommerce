from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.shortcuts import render, redirect
from django.urls import reverse


app_name = 'account'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.LoginView.as_view(), name='login'),

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password/', views.PasswordResetView.as_view(), name='password-reset'),

    path('orders/', views.OrdersView.as_view(), name='orders'),
    path('addresses/', views.AddressesView.as_view(), name='addresses'),

    path('addresses/', views.AddressesView.as_view(), name='addresses'),
    path('delete-address/<int:id>/', views.delete_address, name='delete-address'),


    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('terms-conditions/', views.termsandservices, name='terms'),
]

