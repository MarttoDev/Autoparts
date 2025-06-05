from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Producto, CartItem

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
