from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('actualizar/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('quitar/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('limpiar/', views.limpiar_sesion, name='limpiar_sesion'),
    path('webpay/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('webpay/retorno/', views.retorno_pago, name='retorno_pago'),
    path('webpay/retorno/', views.retorno_pago, name='webpay_retorno'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),



]


