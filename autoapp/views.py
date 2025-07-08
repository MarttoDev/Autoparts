from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import generics
import uuid

#mayorista
from decimal import Decimal
def es_usuario_mayorista(user):
    try:
        return user.perfilusuario.es_mayorista
    except PerfilUsuario.DoesNotExist:
        return False


#panel admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from datetime import datetime


@staff_member_required  # Solo staff y superusuarios pueden acceder
def panel_superusuario(request):
    productos_ref = db.collection('productos').stream()
    productos = [{'id': p.id, **p.to_dict()} for p in productos_ref]

    compras_ref = db.collection('compras').stream()
    compras = []
    for v in compras_ref:
        data = v.to_dict()

        fecha_val = data.get('fecha')
        if fecha_val:
            if isinstance(fecha_val, str):
                try:
                    fecha_obj = datetime.fromisoformat(fecha_val)
                except ValueError:
                    fecha_obj = None
            elif isinstance(fecha_val, datetime):
                fecha_obj = fecha_val
            else:
                fecha_obj = None

            fecha_formateada = fecha_obj.strftime('%Y-%m-%d') if fecha_obj else str(fecha_val)
        else:
            fecha_formateada = 'N/A'

        compras.append({
            'id': v.id,
            'usuario': data.get('usuario', 'N/A'),  
            'fecha': fecha_formateada,
            'total': data.get('total'),
            'items': data.get('items', []),  
        })

    return render(request, 'panel_superusuario.html', {
        'productos': productos,
        'compras': compras,
    })


#firebase
from .firebase_config import db 
from .firebase_services import guardar_compra_en_firebase
from .firebase_services import actualizar_stock_en_firebase

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

#PANEL DE ADMIN
def verificar_superusuario(request):
    es_superusuario = request.user.is_authenticated and request.user.is_superuser
    return render(request, 'pagina_principal.html', {'es_superusuario': es_superusuario})


def index(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    # Verificamos si el usuario es mayorista
    es_mayorista = (
        request.user.is_authenticated and 
        hasattr(request.user, 'perfilusuario') and 
        request.user.perfilusuario.es_mayorista
    )

    # Agregamos precio mayorista dinámico
    for producto in productos:
        if es_mayorista:
            producto.precio_mayorista = producto.precio * Decimal('0.7')
        else:
            producto.precio_mayorista = None  # Opcional, solo para claridad

    context = {
        'productos': productos,
        'categorias': categorias,
        'cart_item_count': request.session.get('cart_item_count', 0),
        'es_mayorista': es_mayorista,
    }
    return render(request, 'index.html', context)


#pal filtro
def productos_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    productos = Producto.objects.filter(categoria=categoria)
    categorias = Categoria.objects.all()
    return render(request, 'index.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria,
    })

#añadir al carrito
@login_required
def add_to_cart(request, product_id):
    producto = get_object_or_404(Producto, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        producto=producto,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')

#registrar usuario
from .models import PerfilUsuario

def register(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            print(form.errors)  # Esto te mostrará los errores en la consola
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})



def cart_view(request):
    return render(request, 'autoapp/cart.html')


from decimal import Decimal

@login_required
def cart_detail(request):
    cart = Cart(request)
    items = cart.get_items()
    total_quantity = sum(item['quantity'] for item in items)

    es_mayorista = (
        request.user.is_authenticated and
        hasattr(request.user, 'perfilusuario') and
        request.user.perfilusuario.es_mayorista
    )

    if es_mayorista and total_quantity < 10:
        messages.error(request, "La compra mínima para mayoristas es de 10 productos.")
        return render(request, 'cart.html', {
            'cart_items': items,
            'cart_total': cart.get_total(),
            'items_count': total_quantity,
            'es_mayorista': es_mayorista,
        })

    total = Decimal('0')
    for item in items:
        if es_mayorista:
            precio_unitario = item['producto'].precio * Decimal('0.7')
        else:
            precio_unitario = item['producto'].precio
        total += precio_unitario * item['quantity']

    return render(request, 'cart.html', {
        'cart_items': items,
        'cart_total': total,
        'items_count': total_quantity,
        'es_mayorista': es_mayorista,
    })




@login_required
def update_cart_quantity(request, producto_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        producto = get_object_or_404(Producto, id=producto_id)
        if quantity > producto.stock:
            messages.error(request, f"Solo quedan {producto.stock} unidades disponibles.")
            quantity = producto.stock
        cart = Cart(request)
        cart.update(producto_id, quantity)
    return redirect('cart_detail')


@login_required
def remove_from_cart(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=producto_id)
    cart.remove(producto)
    return redirect('cart_detail')


@login_required
def guardar_direccion(request):
    if request.method == 'POST':
        campos = ['nombre', 'direccion', 'ciudad', 'codigo_postal', 'telefono']
        if not all(request.POST.get(campo) for campo in campos):
            messages.error(request, "Por favor completa todos los campos de dirección.")
            return redirect('cart_detail')

        request.session['direccion_envio'] = {campo: request.POST.get(campo) for campo in campos}
        messages.success(request, "Dirección guardada correctamente.")
    return redirect('cart_detail')

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



def productos_api(request):
    productos = Producto.objects.all()
    data = [{
        'id': p.id,
        'nombre': p.nombre,
        'marca': p.marca,
        'precio': p.precio,
        'stock': p.stock,
    } for p in productos]
    return JsonResponse(data, safe=False)


class ProductoListAPI(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


def tienda_view(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()

    categorias_filtradas = request.GET.getlist("categorias")
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")

    if categorias_filtradas:
        productos = productos.filter(categoria__id__in=categorias_filtradas)

    try:
        if precio_min:
            productos = productos.filter(precio__gte=float(precio_min))
        if precio_max:
            productos = productos.filter(precio__lte=float(precio_max))
    except ValueError:
        pass

    es_mayorista = request.user.is_authenticated and request.user.groups.filter(name="Mayoristas").exists()

    context = {
        'categorias': categorias,
        'productos': productos,
        'categorias_filtradas': categorias_filtradas,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'cart_item_count': request.session.get('cart_item_count', 0),
        'es_mayorista': es_mayorista,
    }
    return render(request, 'autoapp/index.html', context)


def limpiar_sesion(request):
    request.session.flush()
    return redirect('index')


# Funciones para Firebase (ajusta según tu configuración)

# def guardar_compra_en_firebase(user, items, total, response, direccion_envio):
#     compra_data = {
#         "usuario": user.username,
#         "items": [{"producto": i['producto'].nombre, "cantidad": i['quantity']} for i in items],
#         "total": str(total),
#         "response_pago": response,
#         "direccion_envio": direccion_envio,
#     }
#     # Implementa el guardado en Firebase aquí
#     print("Compra guardada en Firebase:", compra_data)
#
#
# def actualizar_stock_en_firebase(producto):
#     try:
#         # Asegúrate de que `db` está importado y configurado para Firestore
#         doc_ref = db.collection('productos').document(str(producto.id))
#         doc_ref.update({'stock': producto.stock})
#         print(f"Stock actualizado en Firebase para producto {producto.nombre} (ID: {producto.id})")
#     except Exception as e:
#         print(f"Error actualizando stock en Firebase: {e}")
