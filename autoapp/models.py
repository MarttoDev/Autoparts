from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_producto = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=100)
    codigo_marca = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    oferta = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total(self):
        return self.quantity * self.producto.precio
