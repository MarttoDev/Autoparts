from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import generics
import uuid

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

    # Obtener filtros desde la URL
    categorias_filtradas = request.GET.getlist('categorias')  # lista de IDs como strings
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    # Aplicar filtro por categorías
    categorias_filtradas = request.GET.getlist('categorias')

    if categorias_filtradas:
        # Si hay categorías seleccionadas, filtras
        productos = productos.filter(categoria__id__in=categorias_filtradas)
    else:
        # Si no hay categorías seleccionadas, muestras todos y marcas todas las categorías
        categorias_filtradas = [str(cat.id) for cat in categorias]

    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    if precio_min:
        try:
            precio_min_val = float(precio_min)
            if precio_min_val > 0:  # Solo filtrar si es mayor que cero
                productos = productos.filter(precio__gte=precio_min_val)
        except ValueError:
            pass

    if precio_max:
        try:
            precio_max_val = float(precio_max)
            if precio_max_val > 0:  # Solo filtrar si es mayor que cero
                productos = productos.filter(precio__lte=precio_max_val)
        except ValueError:
            pass


    context = {
        'productos': productos,
        'categorias': categorias,
        'categorias_filtradas': categorias_filtradas,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'cart_item_count': request.session.get('cart_item_count', 0),  # si estás usando carrito
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
    return render(request, 'cart.html', {'cart_items': items})


def limpiar_sesion(request):
    request.session.flush()
    return redirect('index')


def iniciar_pago(request):
    cart = Cart(request)
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
    print("\n🔥 Datos recibidos:", request.POST or request.GET)

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
