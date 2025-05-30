# autoapp/cart.py

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        # Aseguramos que el carrito sea un diccionario
        if not isinstance(cart, dict):
            cart = {}
        self.session['cart'] = cart
        self.cart = cart

    def add(self, producto):
        producto_id = str(producto.id)

        if producto_id in self.cart:
            self.cart[producto_id]['quantity'] += 1
        else:
            self.cart[producto_id] = {
                'nombre': producto.nombre,
                'precio': str(producto.precio),  # Guardar como string para evitar errores
                'quantity': 1
            }
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.cart:
            del self.cart[producto_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def __iter__(self):
        from .models import Producto
        producto_ids = self.cart.keys()
        productos = Producto.objects.filter(id__in=producto_ids)

        for producto in productos:
            item = self.cart[str(producto.id)].copy()
            item['producto'] = producto  # Se usa solo aquí, no se guarda en sesión
            item['total'] = float(item['precio']) * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total(self):
        return sum(float(item['precio']) * item['quantity'] for item in self.cart.values())
