
from .cart import Cart

def cart_context(request):
    return {
        'cart_item_count': len(Cart(request))
    }

def carrito_total(request):
    carrito = request.session.get('carrito', {})
    total_items = sum(carrito.values())
    return {'carrito_total_items': total_items}
