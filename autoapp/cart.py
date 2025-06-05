from .models import CartItem, Producto

class Cart:
    def __init__(self, request):
        self.request = request
        self.user = request.user

    def add(self, producto, quantity=1):
        if self.user.is_authenticated:
            item, created = CartItem.objects.get_or_create(user=self.user, producto=producto)
            if not created:
                item.quantity += quantity
            item.save()
        else:
            cart = self.request.session.get('cart', {})
            product_id = str(producto.id)
            cart[product_id] = cart.get(product_id, 0) + quantity
            self.request.session['cart'] = cart

    def get_items(self):
        if self.user.is_authenticated:
            return CartItem.objects.filter(user=self.user)
        else:
            cart = self.request.session.get('cart', {})
            productos = Producto.objects.filter(id__in=cart.keys())
            return [{'producto': p, 'quantity': cart[str(p.id)]} for p in productos]

    def clear(self):
        if self.user.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        else:
            self.request.session['cart'] = {}

    def __len__(self):
        if self.user.is_authenticated:
            return sum(item.quantity for item in CartItem.objects.filter(user=self.user))
        else:
            return sum(self.request.session.get('cart', {}).values())
        
    def get_total(self):
        if self.user.is_authenticated:
            return sum(item.total() for item in CartItem.objects.filter(user=self.user))
        else:
            cart = self.request.session.get('cart', {})
            productos = Producto.objects.filter(id__in=cart.keys())
            return sum(p.precio * cart[str(p.id)] for p in productos)

    def remove(self, producto):
        if self.user.is_authenticated:
            try:
                item = CartItem.objects.get(user=self.user, producto=producto)
                item.delete()
            except CartItem.DoesNotExist:
                pass
        else:
            cart = self.request.session.get('cart', {})
            product_id = str(producto.id)
            if product_id in cart:
                del cart[product_id]
                self.request.session['cart'] = cart

