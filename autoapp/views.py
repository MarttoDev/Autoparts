import uuid
from django.http import HttpResponse
import pprint
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from .cart import Cart
from transbank.webpay.webpay_plus.transaction import Transaction
from django.views.decorators.csrf import csrf_exempt

# Función para obtener una instancia de Transaction en modo integración (sandbox)
def get_transaction():
    return Transaction.build_for_integration(
        commerce_code="597055555532",
        api_key="1234567890abcdef1234567890abcdef"
    )


def index(request):
    productos = Producto.objects.all()
    return render(request, 'index.html', {'productos': productos})

def cart_view(request):
    return render(request, 'autoapp/cart.html')

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
    total = int(cart.get_total())  # ¡Asegúrate de que sea ENTERO!
    
    buy_order = str(uuid.uuid4())[:26]  # Genera una orden única
    session_id = request.session.session_key or str(uuid.uuid4())
    return_url = request.build_absolute_uri('/webpay/retorno/')  # IMPORTANTE: URL absoluta

    transaction = Transaction.build_for_integration(
        commerce_code="597055555532",  # Código de prueba
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"  # API Key de prueba
    )

    try:
        response = transaction.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=total,
            return_url=return_url
        )
        return redirect(f"{response['url']}?token_ws={response['token']}")  # Redirige a WebPay
    except Exception as e:
        return render(request, 'webpay/error.html', {'mensaje': f'Error: {str(e)}'})


@csrf_exempt
def retorno_pago(request):
    # Depuración inmediata (verás esto en la consola de Django)
    print("\n🔥 Datos recibidos:", request.POST or request.GET)
    
    # Maneja tanto POST (éxito) como GET (usuario volvió manualmente)
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    
    if token:
        try:
            transaction = Transaction.build_for_integration(
                commerce_code="597055555532",
                api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
            )
            response = transaction.commit(token)
            
            if response.get("status") == "AUTHORIZED":
                request.session["cart"] = {}
                return render(request, "webpay/exito.html", {"response": response})
            return render(request, "webpay/error.html", {"mensaje": "Pago no autorizado"})
        except Exception as e:
            return render(request, "webpay/error.html", {"mensaje": f"Error: {str(e)}"})
    
    # Si no hay token, muestra una página genérica (para evitar errores)
    return render(request, "webpay/error.html", {
        "mensaje": "Proceso completado. Verifica en Transbank si el pago fue exitoso."
    })