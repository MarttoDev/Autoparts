from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import generics
import uuid
from .firebase_services import guardar_compra_en_firebase
from django.contrib import messages

from .models import Producto, CartItem, Categoria
from .serializers import ProductoSerializer
from .forms import RegistroUsuarioForm
from .cart import Cart
from transbank.webpay.webpay_plus.transaction import Transaction


def get_transaction():
    return Transaction.build_for_integration(
        commerce_code="597055555532",
        api_key="1234567890abcdef1234567890abcdef"
    )


def index(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    es_mayorista = False
    if request.user.is_authenticated and hasattr(request.user, 'perfilusuario'):
        es_mayorista = request.user.perfilusuario.es_mayorista

    # Filtros (ya los tienes)

    # Agregar precio con descuento
    for producto in productos:
        producto.precio_mayorista = producto.precio * 0.7 if es_mayorista else producto.precio

    context = {
        'productos': productos,
        'categorias': categorias,
        'cart_item_count': request.session.get('cart_item_count', 0),
        'es_mayorista': es_mayorista,
    }
    return render(request, 'index.html', context)


def productos_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    productos = Producto.objects.filter(categoria=categoria)
    categorias = Categoria.objects.all()
    return render(request, 'index.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria,  # opcional para marcar la categoría activa en el menú
    })


@login_required
def add_to_cart(request, product_id):
    producto = Producto.objects.get(pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        producto=producto,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')


def register(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})


def cart_view(request):
    return render(request, 'autoapp/cart.html')


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


def remove_from_cart(request, producto_id):
    cart = Cart(request)
    producto = Producto.objects.get(id=producto_id)
    cart.remove(producto)
    return redirect('cart_detail')


def productos_api(request):
    productos = Producto.objects.all()
    data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'marca': p.marca,
            'precio': p.precio,
            'stock': p.stock,
        }
        for p in productos
    ]
    return JsonResponse(data, safe=False)


@login_required
def cart_detail(request):
    cart = Cart(request)
    items = cart.get_items()
    total_quantity = sum(item['quantity'] for item in items)
    
    es_mayorista = False
    if hasattr(request.user, 'perfilusuario'):
        es_mayorista = request.user.perfilusuario.es_mayorista

    if es_mayorista and total_quantity < 10:
        messages.error(request, "La compra mínima para mayoristas es de 10 productos.")
        return redirect('cart_view')  # Cambia esta URL si quieres, para volver a la vista del carrito

    # Calcular total con descuento si aplica
    total = 0
    for item in items:
        precio_unitario = item['producto'].precio
        if es_mayorista:
            precio_unitario *= 0.7  # 30% descuento
        total += precio_unitario * item['quantity']

    return render(request, 'cart.html', {
        'cart_items': items,
        'cart_total': total,
        'items_count': len(items),
        'es_mayorista': es_mayorista,
    })


def limpiar_sesion(request):
    request.session.flush()
    return redirect('index')


@login_required
def iniciar_pago(request):
    cart = Cart(request)
    total_items = sum(item['quantity'] for item in cart.get_items())

    es_mayorista = False
    if request.user.is_authenticated and hasattr(request.user, 'perfilusuario'):
        es_mayorista = request.user.perfilusuario.es_mayorista

    # Validar cantidad mínima para mayoristas
    if es_mayorista and total_items < 10:
        mensaje = "Para usuarios mayoristas la compra mínima es de 10 productos."
        return render(request, 'autoapp/cart.html', {'mensaje_error': mensaje, 'cart_items': cart.get_items(), 'cart_total': cart.get_total()})

    total = int(cart.get_total())

    buy_order = str(uuid.uuid4())[:26]  # Genera una orden única
    session_id = request.session.session_key or str(uuid.uuid4())
    return_url = request.build_absolute_uri('/webpay/retorno/')

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

    token = request.POST.get("token_ws") or request.GET.get("token_ws")

    if token:
        try:
            transaction = Transaction.build_for_integration(
                commerce_code="597055555532",
                api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
            )
            response = transaction.commit(token)

            if response.get("status") == "AUTHORIZED":
                cart = Cart(request)
                items = cart.get_items()
                total = cart.get_total()

                # Obtener dirección guardada en sesión, si existe
                direccion_envio = request.session.get('direccion_envio', {})

                # Guardar compra en Firebase, enviando la dirección también
                guardar_compra_en_firebase(request.user, items, total, response, direccion_envio)

                for item in items:
                    producto = item['producto']
                    cantidad = item['quantity']

                    producto.stock -= cantidad
                    producto.save()

                    actualizar_stock_en_firebase(producto)

                # Limpiar carrito y sesión dirección
                request.session['cart'] = {}
                CartItem.objects.filter(user=request.user).delete()
                if 'direccion_envio' in request.session:
                    del request.session['direccion_envio']

                return render(request, "webpay/exito.html", {"response": response})

            return render(request, "webpay/error.html", {"mensaje": "Pago no autorizado"})

        except Exception as e:
            return render(request, "webpay/error.html", {"mensaje": f"Error: {str(e)}"})

    return render(request, "webpay/error.html", {
        "mensaje": "Proceso completado. Verifica en Transbank si el pago fue exitoso."
    })




class ProductoListAPI(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

def productos_filtrados(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()

    categorias = request.GET.getlist("categorias")
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")


    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)

    if precio_min:
        productos = productos.filter(precio__gte=precio_min)

    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    context = {
        'categorias': categorias,
        'productos': productos,
        'cart_item_count': request.session.get('cart_item_count', 0),
    }
    return render(request, 'autoapp/index.html', context)

def tienda_view(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()

    # Obtener filtros
    categorias_filtradas = request.GET.getlist("categorias")
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")

    # Aplicar filtros
    if categorias_filtradas:
        productos = productos.filter(categoria__id__in=categorias_filtradas)

    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    context = {
        'categorias': categorias,
        'productos': productos,
        'categorias_filtradas': categorias_filtradas,
        'precio_min': precio_min,
        'precio_max': precio_max,
    }
    return render(request, 'autoapp/tienda.html', context)

@login_required
def update_cart_quantity(request, producto_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        producto = Producto.objects.get(id=producto_id)
        if quantity > producto.stock:
            messages.error(request, f"Solo quedan {producto.stock} unidades disponibles.")
            quantity = producto.stock
        cart = Cart(request)
        cart.update(producto_id, quantity)
    return redirect('cart_detail')

@login_required
def guardar_direccion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        telefono = request.POST.get('telefono')

        if not all([nombre, direccion, ciudad, codigo_postal, telefono]):
            messages.error(request, "Por favor completa todos los campos de dirección.")
            return redirect('cart_detail')

        # Guardar en sesión para usar luego en el pago
        request.session['direccion_envio'] = {
            'nombre': nombre,
            'direccion': direccion,
            'ciudad': ciudad,
            'codigo_postal': codigo_postal,
            'telefono': telefono,
        }
        messages.success(request, "Dirección guardada correctamente.")
        return redirect('cart_detail')

    return redirect('cart_detail')

def guardar_compra_en_firebase(user, items, total, response, direccion_envio):
    # Aquí conectas a Firebase y guardas los datos de la compra
    # Por ejemplo:
    compra_data = {
        "usuario": user.username,
        "items": [{"producto": i['producto'].nombre, "cantidad": i['quantity']} for i in items],
        "total": str(total),
        "response_pago": response,
        "direccion_envio": direccion_envio,
    }
    # Código para guardar compra_data en Firebase aquí
    print("Compra guardada en Firebase:", compra_data)


def actualizar_stock_en_firebase(producto):
    """
    Actualiza el stock de un producto en Firestore.
    Asume que tienes una colección 'productos' y documentos con ID igual al ID del producto.
    """
    try:
        doc_ref = db.collection('productos').document(str(producto.id))
        doc_ref.update({
            'stock': producto.stock
        })
        print(f"Stock actualizado en Firebase para producto {producto.nombre} (ID: {producto.id})")
    except Exception as e:
        print(f"Error actualizando stock en Firebase: {e}")