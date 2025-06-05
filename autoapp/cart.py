from decimal import Decimal
from .models import CartItem, Producto

class Cart:
    def __init__(self, request):
        self.request = request
        self.user = request.user

    def add(self, producto, quantity=1):
        if self.user.is_authenticated:
            item, created = CartItem.objects.get_or_create(
                user=self.user, 
                producto=producto
            )
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            item.save()
        else:
            cart = self.request.session.get('cart', {})
            product_id = str(producto.id)
            if product_id in cart:
                cart[product_id]['quantity'] += quantity
            else:
                cart[product_id] = {
                    'quantity': quantity,
                    'price': str(producto.precio),
                    'nombre': producto.nombre
                }
            self.request.session['cart'] = cart

    def get_items(self):
        items = []
        if self.user.is_authenticated:
            for item in CartItem.objects.filter(user=self.user):
                items.append({
                    'producto': item.producto,
                    'quantity': item.quantity,
                    'total': item.producto.precio * item.quantity
                })
        else:
            cart = self.request.session.get('cart', {})
            product_ids = cart.keys()
            productos = Producto.objects.filter(id__in=product_ids)
            for producto in productos:
                product_id = str(producto.id)
                items.append({
                    'producto': producto,
                    'quantity': cart[product_id]['quantity'],
                    'total': producto.precio * cart[product_id]['quantity']
                })
        return items

    def get_total(self):
        return sum(Decimal(str(item['total'])) for item in self.get_items())

    def count(self):
        """Devuelve la cantidad total de items (suma de cantidades)"""
        return sum(item['quantity'] for item in self.get_items())

    def __len__(self):
        """Alias para count() para soportar len(cart)"""
        return self.count()

    def remove(self, producto):
        if self.user.is_authenticated:
            CartItem.objects.filter(
                user=self.user,
                producto=producto
            ).delete()
        else:
            cart = self.request.session.get('cart', {})
            product_id = str(producto.id)
            if product_id in cart:
                del cart[product_id]
                self.request.session['cart'] = cart

    def clear(self):
        if self.user.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        else:
            self.request.session['cart'] = {}