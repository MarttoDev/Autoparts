from .firebase_config import db
from datetime import datetime
from .models import Producto

def guardar_compra_en_firebase(user, cart_items, total, transbank_response, direccion_envio):
    from pprint import pprint
    datos_compra = {
        'usuario': user.username,
        'email': user.email,
        'fecha': datetime.utcnow().isoformat(),
        'total': int(total),
        'items': [
            {
                'producto_id': item['producto'].id,
                'nombre': item['producto'].nombre,
                'precio': int(item['producto'].precio),
                'cantidad': item['quantity']
            }
            for item in cart_items
        ],
        'transbank_status': transbank_response.get("status"),
        'orden': transbank_response.get("buy_order"),
        'direccion_envio': direccion_envio
    }

    print("➡️ Datos que se enviarán a Firebase:")
    pprint(datos_compra)

    try:
        result = db.collection('compras').add(datos_compra)
        print(f"✅ Compra guardada con ID: {result[1].id}")
    except Exception as e:
        print("❌ ERROR guardando en Firebase:", e)


def guardar_producto_en_firebase(producto):
    doc_ref = db.collection('productos').document(str(producto.id))
    doc_ref.set({
        'nombre': producto.nombre,
        'marca': producto.marca,
        'precio': round(float(producto.precio)),  
        'stock': producto.stock,
        'descripcion': producto.descripcion,
        'categoria_id': producto.categoria.id if producto.categoria else None,
        'categoria_nombre': producto.categoria.nombre if producto.categoria else None,
    })
    print("Productos subidos a Firebase")

def eliminar_producto_de_firebase(producto_id):
    db.collection('productos').document(str(producto_id)).delete()

def actualizar_stock_en_firebase(producto):
    doc_ref = db.collection('productos').document(str(producto.id))
    doc_ref.update({'stock': producto.stock})
