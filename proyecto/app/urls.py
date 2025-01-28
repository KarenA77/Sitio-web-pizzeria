from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import CustomPasswordResetConfirmView
from . import views

urlpatterns = [
    path('menu/', views.store, name = 'Tienda'),
    path('cart/', views.cart, name = 'Carrito'),
    path('checkout/', views.checkout, name = 'Pago'),
    path('update_item/', views.updateItem, name = 'update_item'),
    path('process_order/', views.processOrder, name = 'process_order'),
    path('menu/login/', views.login_view, name='login'),
    path('menu/register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register_view, name='register'),

   # Rutas para recuperación de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='generales/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='generales/password_reset_done.html'), name='password_reset_done'),
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='generales/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='generales/password_reset_complete.html'), name='password_reset_complete'),
    #path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('', views.inicio, name='inicio'),
    ]