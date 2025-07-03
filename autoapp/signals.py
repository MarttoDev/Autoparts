from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Producto, CartItem
from django.db.models.signals import post_save, post_delete
from .firebase_services import guardar_producto_en_firebase, eliminar_producto_de_firebase
from .models import PerfilUsuario
from django.contrib.auth.models import User

@receiver(user_logged_in)
def transfer_session_cart(sender, request, user, **kwargs):
    session_cart = request.session.get('cart', {})
    for product_id, quantity in session_cart.items():
        try:
            producto = Producto.objects.get(id=product_id)
            item, created = CartItem.objects.get_or_create(user=user, producto=producto)
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            item.save()
        except Producto.DoesNotExist:
            continue
    # Vaciar el carrito de sesión
    request.session['cart'] = {}

# Cuando se guarda o actualiza un producto
@receiver(post_save, sender=Producto)
def producto_guardado(sender, instance, **kwargs):
    guardar_producto_en_firebase(instance)

# Cuando se elimina un producto
@receiver(post_delete, sender=Producto)
def producto_eliminado(sender, instance, **kwargs):
    eliminar_producto_de_firebase(instance.id)


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)
