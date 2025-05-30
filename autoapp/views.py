import uuid
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .cart import Cart
from transbank.webpay.webpay_plus.transaction import Transaction
from django.views.decorators.csrf import csrf_exempt

# Usa el método build_for_integration sin pasar credenciales para modo test
transaction = Transaction.build_for_integration(
    commerce_code='597055555532',
    api_key='9d4f5383f13b4f8b987a787c5e54589d'
)

def index(request):
    productos = Producto.objects.all()
    return render(request, 'index.html', {'productos': productos})

def add_to_cart(request, product_id):
    producto = get_object_or_404(Producto, pk=product_id)
    cart = Cart(request)
    cart.add(producto)
    return redirect('index')

def update_cart_item(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[str(product_id)] = quantity
        else:
            cart.pop(str(product_id), None)
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'autoapp/cart.html', {
        'cart_items': list(cart),
        'cart_total': cart.get_total()
    })

def limpiar_sesion(request):
    request.session.flush()
    return redirect('index')

def iniciar_pago(request):
    cart = Cart(request)
    total = int(cart.get_total())  # <-- asegúrate que sea int

    if total <= 0:
        return render(request, 'webpay/error.html', {'mensaje': 'El carrito está vacío.'})

    buy_order = str(uuid.uuid4()).replace('-', '')[:26]

    # Forzar generación de session_key si no existe
    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key

    return_url = request.build_absolute_uri('/webpay/retorno/')

    try:
        response = transaction.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=total,
            return_url=return_url
        )
    except Exception as e:
        return render(request, 'webpay/error.html', {'mensaje': f'Error al crear transacción: {e}'})

    token = response.token
    url = response.url

    return redirect(f"{url}?token_ws={token}")

@csrf_exempt
def retorno_pago(request):
    token = request.POST.get("token_ws")

    if not token:
        return render(request, "webpay/error.html", {"mensaje": "Token no recibido."})

    try:
        response = transaction.commit(token)
    except Exception as e:
        return render(request, "webpay/error.html", {"mensaje": f"Error al confirmar pago: {e}"})

    if response.status == 'AUTHORIZED':
        request.session['cart'] = {}
        return render(request, "webpay/exito.html", {"response": response})
    else:
        return render(request, "webpay/error.html", {"mensaje": "Pago no autorizado."})
