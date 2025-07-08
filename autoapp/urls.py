from django.urls import path, include
from . import views
from .views import ProductoListAPI
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('quitar/<int:producto_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('limpiar/', views.limpiar_sesion, name='limpiar_sesion'),
    path('webpay/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('webpay/retorno/', views.retorno_pago, name='retorno_pago'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('api/productos/', ProductoListAPI.as_view(), name='api-productos'),
    path('categoria/<str:nombre>/', views.productos_por_categoria, name='categoria'),
    path('productos/categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('categoria/<slug:slug>/', views.productos_por_categoria, name='categoria'),
    path('cart/update/<int:producto_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('guardar-direccion/', views.guardar_direccion, name='guardar_direccion'),
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('carrito/', views.cart_view, name='cart_view'),
    path('guardar-direccion/', views.guardar_direccion, name='guardar_direccion'),
    path('superusuario/', views.panel_superusuario, name='pagina_superusuario'),

  


]


