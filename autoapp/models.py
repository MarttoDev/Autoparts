from django.db import models

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
    imagen = models.URLField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    oferta = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
